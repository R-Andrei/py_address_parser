import re
import usaddress as usa
from Address import Address
from Component import Component
from ComponentContainer import ComponentContainer
from copy import deepcopy
from converter import to_digits

class Parser:
    """
    NOT DOCUMENTED YET.

    Usage of Parser class:

    -define parser object like 'parser = Parser()'
    -optionally define settings, using methods: set_valid_address_settings, set_street_type_settings, set_all_street_type_settings, set_direction_type_settings
    -call 'parse_address' method, assign result to a variable like 'my_address = parser.parse_address(address)'

    *Parser returns Address type objects.
    """
    def __init__(self, *args, **kwargs):

        #address storage
        self.address = None
        self.usaddress_components = ComponentContainer()
        self.parsed_address = Address()

        #valid address settings
        self.valid_address_template = {
            'AddressNumber'         : False,        'StreetNamePreDirectional'  : False,
            'StreetNamePreType'     : False,        'StreetName'                : False,
            'StreetNamePostType'    : False,        'StreetNamePostDirectional' : False,
            'PlaceName'             : False,        'StateName'                 : False,
            'ZipCode'               : False,        'ZipCodeExtension'          : False
        }
        self.valid = self.validate_address()

        #components to be checked frequently
        self.check_components = ('StreetNamePostType', 'StreetNamePreType', 'StreetNamePreDirectional', 'StreetNamePostDirectional')
        self.street_directions = self.check_components[2:]

        #state conversion
        self.state_converter = {
            'alabama'       : 'AL', 'alaska'        : 'AK', 'arizona'     : 'AZ', 'arkansas'      : 'AR', 
            'california'    : 'CA', 'georgia'       : 'GA', 'iowa'        : 'IA', 'maryland'      : 'MD', 
            'colorado'      : 'CO', 'connecticut'   : 'CT', 'delaware'    : 'DE', 'florida'       : 'FL', 
            'hawaii'        : 'HI', 'idaho'         : 'ID', 'illinois'    : 'IL', 'indiana'       : 'IN', 
            'kansas'        : 'KS', 'kentucky'      : 'KY', 'louisiana'   : 'LA', 'maine'         : 'ME', 
            'massachusetts' : 'MA', 'michigan'      : 'MI', 'minnesota'   : 'MN', 'mississippi'   : 'MS', 
            'missouri'      : 'MO', 'montana'       : 'MT', 'nebraska'    : 'NE', 'nevada'        : 'NV', 
            'newjersey'     : 'NJ', 'newmexico'     : 'NM', 'newyork'     : 'NY', 'northcarolina' : 'NC', 
            'northdakota'   : 'ND', 'ohio'          : 'OH', 'oklahoma'    : 'OK', 'oregon'        : 'OR', 
            'rhodeisland'   : 'RI', 'southcarolina' : 'SC', 'southdakota' : 'SD', 'tennessee'     : 'TN', 
            'texas'         : 'TX', 'utah'          : 'UT', 'vermont'     : 'VT', 'virginia'      : 'VA', 
            'washington'    : 'WA', 'westvirginia'  : 'WV', 'wisconsin'   : 'WI', 'wyoming'       : 'WY',
            'newhampshire'  : 'NH', 'pennsylvania'  : 'PA', 'puertorico'  : 'PR'
        }

        #direction conversion
        self.direction_names = {
            True  : ['N',       'E',      'S',       'W',      'NE',          'NW',          'SE',          'SW'       ],
            False : ['North',   'East',   'South',   'West',   'Northeast',   'Northwest',   'Southeast',   'Southwest']
        }
        self.direction_converter = {
            'north.n'      : None,
            'east.e'       : None,
            'south.s'      : None,
            'west.w'       : None,
            'northeast.ne' : None,
            'northwest.nw' : None,
            'southeast.se' : None,
            'southwest.sw' : None
        }
        self.set_direction_type_settings()

        #street type conversion
        self.street_type_converter = {
            'alley'         : 'alley.aly.allee.ally',               'annex'         : 'annex.anx.anex.annx',
            'arcade'        : 'arcade.arc.arcades.arcs',            'avenue'        : 'avenue.ave.av.aven.avenu.avn.avnue',
            'bluff'         : 'bluff.blf.blfs.bluf.bluffs',         'bottom'        : 'bottom.bot.bottm.btm',
            'boulevard'     : 'boulevard.blvd.boulv.boul',          'branch'        : 'branch.br.brnch',
            'bridge'        : 'bridge.brg.brdge',                   'bypass'        : 'bypass.byps.byp.bypa.bypas',
            'causeway'      : 'causeway.cswy.causwa.causewy.csway', 'center'        : 'center.cen.cent.centers.centr.centre.cnter.cntr.ctr',
            'cliff'         : 'cliff.clf.clfs.cliffs',              'circle'        : 'circle.cir.circ.circl.circles.cirs.crcl.crcle',
            'court'         : 'court.ct.courts.crt.cts',            'cove'          : 'cove.cv.cve.coves',
            'curve'         : 'curve.cv.curv.cvs',                  'crescent'      : 'crescent.cres.crest.crse.crsent.crsnt.crst',
            'drive'         : 'drive.dr.driv.drives.drs.drv.dv',    'estate'        : 'estate.est.estates.ests',
            'fork'          : 'fork.frk.forks.frks',                'expressway'    : 'expressway.expwy.exp.expr.express.expw.expy',
            'freeway'       : 'freeway.fwy.freewy.frway.frwy.fry',  'extension'     : 'extension.ext.extensions.extn.extnsn.exts',
            'gateway'       : 'gateway.gtwy.gatewy.gatway.gtway',   'garden'        : 'garden.gdn.gardens.gardn.gdns.grden.grdn.grdns',
            'grove'         : 'grove.grv.grov.groves.grvs',         'harbor'        : 'harbor.hbr.harb.harbors.harbr.hbrs.hrbor.hrbr',
            'hill'          : 'hill.hl.hills.hls',                  'hollow'        : 'hollow.hlw.hollows.holw.holws.hllw.holw.holws',
            'island'        : 'island.islnd.island.islnds.iss',     'isle'          : 'isle.is.isles.',
            'key'           : 'key.key.keys.ky.kys',                'junction'      : 'junction.jctn.jct.jctns.jcts.junctions.junctn.juncton',
            'landing'       : 'landing.land.lndg.lndng',            'lane'          : 'lane.ln.lne.lanes.lnes.lns.lans',
            'loop'          : 'loop.loop.loops',                    'meadow'        : 'meadow.mdw.mdws.meadows.medows', 
            'mhp'           : 'mhp.mhp',                            'mill'          : 'mill.ml.mills.mls.mils',
            'park'          : 'park.park.parks.prks.prk',           'mountain'      : 'mountain.mt.mount.mountains.mountin.mtin.mtn.mtns.mtwy',
            'place'         : 'place.pl.pls.places',                'parkway'       : 'parkway.pkwy.parkways.parkwy.pkway.pkwys.pky',
            'plain'         : 'plain.pln.plains.plns',              'turnpike'      : 'turnpike.tpke.pike.turnpk.pikes.pke.pkes',
            'plz'           : 'plz.plz',                            'passage'       : 'passage.pass.passages.psg.psgs.psge',
            'port'          : 'port.prt.ports.prts',                'point'         : 'point.pt.pointe.points.pointes.ptes.pts',
            'radial'        : 'radial.rad.radiel.radl',             'ranch'         : 'ranch.rnch.ranches.rnchs',
            'ridge'         : 'ridge.rdg.rdge.rdgs.ridges.rdges',   'road'          : 'road.rd.roads.rds',
            'route'         : 'route.rte.rue.routes.rtes.rt.rts',   'river'         : 'river.riv.rivr.rvr.rivers.rivrs.rvrs',
            'shore'         : 'shore.shr.shoar.shoars.shore.shrs',  'spring'        : 'spring.spg.spgs.spng.spngs.springs.sprng.sprngs',
            'station'       : 'station.stn.sta.statn',              'square'        : 'square.sq.sqr.sqre.sqrs.sqs.squ.squares',
            'trail'         : 'trail.trl',                          'street'        : 'street.st.str.stra.streets.strt.strts',
            'trce'          : 'trce.trce.',                         'terrace'       : 'terrace.ter.terr.terace.trc.ters.terraces.terrs',
            'trafficway'    : 'trafficway.trfwy.trfy.trfwys',       'tunnel'        : 'tunnel.tnl.tunel.tunl.tunls.tunnel.tunnels.tunnl',
            'way'           : 'way.wy.wys.ways',                    'valley'        : 'valley.valley.vly.valleys.vally.vallys.vlys.vlly',
            'village'       : 'village.vill.villag.villages.ville.villg.villiage.vlg',
            'highway'       : 'highway.hwy.highwy.hiway.hiwy.hway.motorway.motorwy.mtrway.throughway.thruway.thruways.thrwy'
        }
        self.street_type_settings = {
            'alley'         : False, 'annex'        : False, 'arcade'   : False, 'avenue'       : False, 'bluff'        : False, 
            'bottom'        : False, 'boulevard'    : False, 'branch'   : False, 'bridge'       : False, 'bypass'       : False, 
            'causeway'      : False, 'center'       : False, 'circle'   : False, 'cliff'        : False, 'court'        : False, 
            'cove'          : False, 'crescent'     : False, 'curve'    : False, 'drive'        : False, 'estate'       : False, 
            'expressway'    : False, 'extension'    : False, 'fork'     : False, 'freeway'      : False, 'garden'       : False, 
            'gateway'       : False, 'grove'        : False, 'harbor'   : False, 'highway'      : False, 'hill'         : False, 
            'hollow'        : False, 'island'       : False, 'isle'     : False, 'junction'     : False, 'key'          : False, 
            'landing'       : False, 'lane'         : False, 'loop'     : False, 'meadow'       : False, 'mhp'          : False, 
            'mill'          : False, 'mountain'     : False, 'park'     : False, 'parkway'      : False, 'passage'      : False, 
            'turnpike'      : False, 'place'        : False, 'plain'    : False, 'plz'          : False, 'point'        : False, 
            'port'          : False, 'radial'       : False, 'ranch'    : False, 'ridge'        : False, 'road'         : False, 
            'route'         : False, 'river'        : False, 'shore'    : False, 'spring'       : False, 'square'       : False, 
            'street'        : False, 'station'      : False, 'terrace'  : False, 'trail'        : False, 'trce'         : False, 
            'trafficway'    : False, 'tunnel'       : False, 'valley'   : False, 'village'      : False, 'way'          : False
        }
        self.street_types = tuple(self.street_type_settings.keys())

    def parse_address(self, address):
        """Parse a single address."""
        self.reset_parser()
        try:
            #store new address
            self.address = address 

            #populate usaddress component container
            self.parse_to_component_container() 

            #create parsed address using parsed components
            self.parsed_address.initialize_address(self.usaddress_components)

            #attempt to resolve remaining inconsistencies
            self.resolve_undefined()
            self.resolve_street_name()
            self.resolve_address_number()

            #decide address validity
            self.valid = self.validate_address()
        except Exception as e:
            self.reset_parser()
            raise Exception(str(e))

        # print(self.address)
        # print(self.parsed_address.address)

        #get result and reset variables
        result = deepcopy(self.send_result())
        self.reset_parser()
        return result

    #Address validity settings
    def set_valid_address_settings(self, *args, **kwargs):
        """
        Description
        -----------
        >Modifies validity settings for address. Has default state.

        Parameters
        ----------
        >
        """
        invalid_container = []
        for key, value in kwargs.items(): ###NOT DONE
            if key in self.parsed_address.keys: ### NOT DONE
                if type(value) == bool: ###NOTDONE
                    self.valid_address_template[key] = value ###NOTDONE 
                else:
                    raise TypeError('Value of ' + key + ' is incorrect, must be either True or False, not ' + str(value)) 
            else:
                invalid_container.append(key)

        if invalid_container:
            raise Exception('Invalid settings:', str(invalid_container))
            
    #Street type settings
    def get_street_type_settings(self, *args):
        for arg in args:
            if arg in self.street_types:
                yield arg, self.street_type_settings[arg]
    
    def set_street_type_settings(self, *args, **kwargs):
        for key, value in kwargs.items():
            if key in self.street_types:
                if type(value) == bool:
                    self.street_type_settings[key] = value
                else:
                    raise TypeError('Type should be boolean. ' + "'" + str(value) + "'" + ' not accepted.')
            else:
                raise ValueError('Street type ' + "'" + str(key) + "'" + ' does not exist.')
    
    def get_all_street_type_settings(self):
        for key, value in self.street_type_settings.items():
            yield key, value

    def set_all_street_type_settings(self, abbrev=False):
        for key, _ in self.street_type_settings.items():
            self.street_type_settings[key] = abbrev

    ### START street direction settings
    def set_direction_type_settings(self, single=False, dual=True):
        #set single
        for index, key in enumerate(list(self.direction_converter.keys())[:4]):
            self.direction_converter[key] = self.direction_names[single][index]
        #set dual
        for index, key in enumerate(list(self.direction_converter.keys())[4:]):
            self.direction_converter[key] = self.direction_names[dual][index+4]

    def get_type_variations(self, *args):
        """Returns an iterable of street type variations for given street types."""
        for arg in args:
            if arg in self.street_types:
                yield self.street_type_converter[arg]

    def standardize_direction(self, direction):
        for direction_type, standard_direction in self.direction_converter.items():
            direction_type = direction_type.split('.')
            for item in direction_type:
                if item == re.sub('[^a-zA-Z]+', '', direction).lower():
                    return standard_direction
        return None

    def check_existing_street_type(self):
        """Returns True if any street type exists in the current address, False otherwise."""
        return True if self.parsed_address['StreetNamePreType'] or self.parsed_address['StreetNamePostType'] else True

    # UTILITY METHODS
    def strip_item(self, item):
        """Remove non digit, non letter characters from string."""
        return re.sub('[^0-9a-zA-Z]+', '', item)
   
    def get_numeric_address_number(self, AddressNumber):
        """Return numeric representation of number if number is initially a word."""
        return str(to_digits(AddressNumber)) if not AddressNumber.isnumeric() else AddressNumber

    # METHODS THAT SHOULD NOT BE CALLED AT ALL
    def resolve_street_name(self):
        """
        Description
        -----------
        >Checks for issues in street name, tries to resolve if any exist.
        """

        function_component = 'StreetName'

        #if street name is missing -> try to get one from other components
        if not self.parsed_address[function_component]:
            for component in self.check_components:
                if self.parsed_address[component]:

                    #avoid using direction components if there is no existing street type component
                    if component in self.street_directions and not self.check_existing_street_type():
                        pass
                    
                    #if valid component found, switch values and break
                    else:
                        self.parsed_address.switch_components(first_component=function_component, second_component=component)
                        break
        
        #if street name is numeric 
        if self.strip_item(self.parsed_address[function_component].value).isnumeric():

            #if there is no pre-street type or pre-street type is like 'road' or 'street' -> remove street name
            if (
                not self.check_existing_street_type() 
                or ( 
                    self.parsed_address['StreetNamePreType']
                    and self.strip_item(self.parsed_address['StreetNamePreType'].value).lower() in '.'.join(self.get_type_variations('road', 'street'))
                )
            ): self.parsed_address.clear_address_component(function_component)

    def resolve_address_number(self):
        #if state is NY check for composed address number
        if self.parsed_address['AdditionalAddressNumber'].exists() and self.parsed_address['StateName'].value == 'NY':
            self.parsed_address['AddressNumber'] = '{AddressNumber}-{AdditionalAddressNumber}'\
                .format(
                    AddressNumber=self.parsed_address['AddressNumber'].value,
                    AdditionalAddressNumber=self.parsed_address['AdditionalAddressNumber'].value
                        )
            self.parsed_address.clear_address_component('AdditionalAddressNumber')
        
        #if address number does not contain digits remove
        if re.sub(r'\D', '', self.parsed_address['AddressNumber'].value) < re.sub(r'\d', '', self.parsed_address['AddressNumber'].value):
            self.parsed_address.clear_address_component('AddressNumber')

    def check_hyphen_name(self, item1, item2):
        if item1.isnumeric() and (item2.upper() in tuple(self.state_converter.values()) or item2.lower() == 'us'):
            return '{item2}-{item1}'.format(item1=item1, item2=item2)
        return None

    def parse_to_component_container(self):
        
        #iterate through each address component
        usaddress = self.state_merge(usa.parse(self.address)) 
        for item in usaddress: 
            #resolve AddressNumber conflicts
            if item[1] == 'AddressNumber':  
                if 'AddressNumber' not in self.usaddress_components:
                    item[0] = re.sub('[^0-9a-zA-Z-]+', '-', item[0])
                    if '-' in item[0] and self.strip_item(item[0]).isnumeric():
                        component_values = item[0].split('-')
                        self.append_address_components(Component(item[1], self.get_numeric_address_number(component_values[0])))
                        for sub_component in component_values[1:]:
                            self.append_address_components(Component('AdditionalAddressNumber', self.strip_item(sub_component)))
                    else:
                        self.append_address_components(Component(item[1], self.get_numeric_address_number(item[0])))
                #if more than one AddressNumber, change one to UndefinedNumber
                else:
                    self.append_address_components(Component('UndefinedNumber', self.strip_item(item[0])))
            
            #street name capitalization and character stripping
            elif item[1] == 'StreetName':
                if '-' in item[0]:
                    split_item = item[0].split('-')
                    if len(split_item) == 2:
                        component_item = self.check_hyphen_name(item1=self.strip_item(split_item[0]), item2=self.strip_item(split_item[1]))
                        component_item = component_item if component_item else self.check_hyphen_name(
                            item1=self.strip_item(split_item[1]), 
                            item2=self.strip_item(split_item[0])
                            )
                        if component_item:
                            self.append_address_components(Component(self.strip_item(item[1]), component_item))
                        else:
                            self.append_address_components(Component(self.strip_item(item[1]), self.strip_item(item[0]).capitalize()))
                    else:
                        self.append_address_components(Component(self.strip_item(item[1]), self.strip_item(split_item[0]).capitalize()))
                else:
                    self.append_address_components(Component(self.strip_item(item[1]), self.strip_item(item[0]).capitalize()))
            #building numbers
            elif item[1] == 'SubaddressIdentifier': 
                if 'AddressNumber' not in self.usaddress_components:
                    self.append_address_components(Component('AddressNumber', self.get_numeric_address_number(item[0])))
                else:
                    self.append_address_components(Component('UndefinedNumber', self.strip_item(item[0])))

            #standardize predirection and postdirection
            elif item[1] == 'StreetNamePreDirectional' or item[1] == 'StreetNamePostDirectional': 
                self.append_address_components(Component(item[1], self.standardize_direction(item[0])))

            #standardize street types
            elif item[1] == 'StreetNamePreType' or item[1] == 'StreetNamePostType':
                item[0] = self.standardize_street_component(component=self.decide_street_component(component=self.strip_item(item[0])))
                self.append_address_components(Component(item[1], item[0]))

            #standardize state name to abbreviated format
            elif item[1] == 'StateName' and len(item[0])>2: 
                if ',' in item[0]:
                    for split_state in item[0].split(','):
                        self.parse_state_component(component=split_state)
                else:
                    self.parse_state_component(component=item[0])

            #if zipcode contains extension, create two components
            elif item[1] == 'ZipCode' and '-' in item[0]: 
                split_item = item[0].split('-')
                self.append_address_components(Component('ZipCode', self.strip_item(split_item[0])))
                self.append_address_components(Component('ZipCodeExtension', self.strip_item(split_item[1])))

            #if number found other than AddressNumber or ZipCode
            elif (item[1] != 'AddressNumber' and item[1] != 'ZipCode') and item[0].isnumeric():
                self.append_address_components(Component('UndefinedNumber', self.strip_item(item[0])))

            #add to dictionary as standard
            else:
                self.append_address_components(Component(self.strip_item(item[1]), self.strip_item(item[0])))

    def parse_state_component(self, component): 
        """
        Description
        -----------
        >Adds a component to the parsed_dictionary based on whether it's a state or not.

        Parameters
        ----------
        >component -> value of a component, if state-like, then add as a state component, otherwise as undefined
        """
        stripped_component = re.sub('[^a-zA-Z]+', '', component).lower()
        if stripped_component in self.state_converter.keys():
            self.append_address_components(Component(component_name='StateName', component_value=self.state_converter[stripped_component]))
        else:
            self.append_address_components(Component(component_name='UndefinedString', component_value=self.strip_item(component).capitalize()))

    def resolve_undefined(self):
        """
        Description
        -----------
        >Iterate through existing undefined components, call self.resolve_undefined_instance for each separate component.
        """
        #iterate through all undefined components of all types
        for undefined_item_type in ['UndefinedNumber', 'UndefinedString']:
            if undefined_item_type in self.usaddress_components:
                #if multiple undefined components of the same type, split
                if ' ' in self.usaddress_components[undefined_item_type].value:
                    for undefined_split in self.usaddress_components[undefined_item_type].value.split(' '):
                        self.resolve_undefined_instance(undefined_type=undefined_item_type, undefined_component=undefined_split)

                else: self.resolve_undefined_instance(undefined_type=undefined_item_type, undefined_component=self.usaddress_components[undefined_item_type].value)

    def resolve_undefined_instance(self, undefined_type, undefined_component):
        """
        Description
        -----------
        >Assign a single undefined component to another component based on type.

        Parameters
        ----------
        >undefined_type -> type of undefined component

        >undefined_component -> the undefined component
        """  
        #if type is number -> use it as street name or address number
        if undefined_type == 'UndefinedNumber':
            if not self.parsed_address['StreetName']:
                self.parsed_address['StreetName'] = undefined_component
            elif not self.parsed_address['AddressNumber']:
                self.parsed_address['AddressNumber'] = undefined_component
        
        #if type is string and there is no city, use it as city
        elif undefined_type == 'UndefinedString':
            if not self.parsed_address['PlaceName']:
                self.parsed_address['PlaceName'] = undefined_component


    #TODO: create better method
    def state_merge(self, usaddress_list):
        """
        Description
        -----------
        >Iterate through output of usaddress.parse, change immutable types to mutables and merge state names if multiple.

        Parameters
        ----------
        >usaddress_list -> list of (component, value) tuples (output of usaddress.parse function)

        Output
        ------
        >Tuple containing lists of [component, value] pairs.
        """

        found, position = False, None

        #change immutable sub-sets to mutables
        for index in range(len(usaddress_list)):
            usaddress_list[index] = list(usaddress_list[index])

        #merge state names if multiple
        for index, item in enumerate(usaddress_list):
            if item[1] == 'StateName' and found == False:
                found, position = True, index
            elif item[1] == 'StateName' and found == True:
                usaddress_list[position][0] += ' ' + item[0]
                del usaddress_list[index]
                position = index
        
        return tuple(usaddress_list)

    # PARSE ADDRESS MAIN LOOP
    def reset_parser(self): 
        """Reset all variables to initial values"""
        self.usaddress_components.clear()
        self.address = None
        self.parsed_address.clear_address()
        self.valid = self.validate_address()
        # print(self.usaddress_components, self.parsed_address, self.valid)

    def validate_address(self):
        """Check whether current address is valid or not. If valid, set valid variable to True."""
        for setting, value in self.valid_address_template.items():
            if value and not self.parsed_address[setting].value:
                return False#if one component missing return; self.valid remains False. 
        return True

    def send_result(self):
        """Return results of parse_address if address is valid. Raises exception if address is not valid."""
        if self.valid:
            return self.parsed_address
        raise Exception('Invalidd address.')
    

    def append_address_components(self, component):
        if not self.usaddress_components.has_component(component):
            self.usaddress_components[component.name] = component
        else:
            self.usaddress_components[component.name].value += ' ' + component.value

    #Street type standardization
    def standardize_street_component(self, component):
        if component in self.street_types:
            if self.street_type_settings[component]:
                return self.street_type_converter[component].split('.')[1].capitalize()
            return self.street_type_converter[component].split('.')[0].capitalize()
        else:
            return component.capitalize()

    def decide_street_component(self, component):
        for key, value in self.street_type_converter.items():
            component_types = value.split('.')
            for component_type in component_types:
                if component_type == component.lower():
                    return key
        return component

