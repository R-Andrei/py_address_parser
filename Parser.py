import re
import usaddress as usa
from Address import Address
from copy import deepcopy
from word_number_converter import word_to_num

class Parser:
    def __init__(self, *args, **kwargs):

        #valid address settings
        self.valid_address_template = {}
        self.initiate_valid_address_settings()
        self.valid = False

        #address storage
        self.address = None
        self.parsed_dictionary = {}
        self.parsed_address = Address({})

        #components to street name
        self.check_components = ['StreetNamePostType', 'StreetNamePreType', 'StreetNamePreDirectional', 'StreetNamePostDirectional']
        self.street_directions = self.check_components[2:]

        #converting states
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

        #converting directions
        self.direction_names = {
            True  : ['N', 'E', 'S', 'W', 'NE', 'NW', 'SE', 'SW'],
            False : ['North', 'East', 'South', 'West', 'Northeast', 'Northwest', 'Southeast', 'Southwest']
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
        self.set_direction_type_abbreviated()

        # STREET TYPE CONVERSION
        self.street_type_converter ={
            'alley'         : 'alley.aly.allee.ally',
            'annex'         : 'annex.anx.anex.annx',
            'arcade'        : 'arcade.arc.arcades.arcs',
            'avenue'        : 'avenue.ave.av.aven.avenu.avn.avnue',
            'bluff'         : 'bluff.blf.blfs.bluf.bluffs',
            'bottom'        : 'bottom.bot.bottm.btm',
            'boulevard'     : 'boulevard.blvd.boulv.boul',
            'branch'        : 'branch.br.brnch',
            'bridge'        : 'bridge.brg.brdge',
            'bypass'        : 'bypass.byps.byp.bypa.bypas',
            'causeway'      : 'causeway.cswy.causwa.causewy.csway',
            'center'        : 'center.cen.cent.centers.centr.centre.cnter.cntr.ctr',
            'circle'        : 'circle.cir.circ.circl.circles.cirs.crcl.crcle',
            'cliff'         : 'cliff.clf.clfs.cliffs',
            'court'         : 'court.ct.courts.crt.cts',
            'cove'          : 'cove.cv.cve.coves',
            'crescent'      : 'crescent.cres.crest.crse.crsent.crsnt.crst',
            'curve'         : 'curve.cv.curv.cvs',
            'drive'         : 'drive.dr.driv.drives.drs.drv.dv',
            'estate'        : 'estate.est.estates.ests',
            'expressway'    : 'expressway.expwy.exp.expr.express.expw.expy',
            'extension'     : 'extension.ext.extensions.extn.extnsn.exts',
            'fork'          : 'fork.frk.forks.frks',
            'freeway'       : 'freeway.fwy.freewy.frway.frwy.fry',
            'garden'        : 'garden.gdn.gardens.gardn.gdns.grden.grdn.grdns',
            'gateway'       : 'gateway.gtwy.gatewy.gatway.gtway',
            'grove'         : 'grove.grv.grov.groves.grvs',
            'harbor'        : 'harbor.hbr.harb.harbors.harbr.hbrs.hrbor.hrbr',
            'highway'       : 'highway.hwy.highwy.hiway.hiwy.hway.motorway.motorwy.mtrway.throughway.thruway.thruways.thrwy',
            'hill'          : 'hill.hl.hills.hls',
            'hollow'        : 'hollow.hlw.hollows.holw.holws.hllw.holw.holws',
            'island'        : 'island.islnd.island.islnds.iss',
            'isle'          : 'isle.is.isles.',
            'junction'      : 'junction.jctn.jct.jctns.jcts.junctions.junctn.juncton',
            'key'           : 'key.key.keys.ky.kys',
            'landing'       : 'landing.land.lndg.lndng',
            'lane'          : 'lane.ln.lne.lanes.lnes.lns.lans',
            'loop'          : 'loop.loop.loops',
            'meadow'        : 'meadow.mdw.mdws.meadows.medows',
            'mhp'           : 'mhp.mhp',
            'mill'          : 'mill.ml.mills.mls.mils',
            'mountain'      : 'mountain.mt.mount.mountains.mountin.mtin.mtn.mtns.mtwy',
            'park'          : 'park.park.parks.prks.prk',
            'parkway'       : 'parkway.pkwy.parkways.parkwy.pkway.pkwys.pky',
            'passage'       : 'passage.pass.passages.psg.psgs.psge',
            'turnpike'      : 'turnpike.tpke.pike.turnpk.pikes.pke.pkes',
            'place'         : 'place.pl.pls.places',
            'plain'         : 'plain.pln.plains.plns',
            'plz'           : 'plz.plz',
            'point'         : 'point.pt.pointe.points.pointes.ptes.pts',
            'port'          : 'port.prt.ports.prts',
            'radial'        : 'radial.rad.radiel.radl',
            'ranch'         : 'ranch.rnch.ranches.rnchs',
            'ridge'         : 'ridge.rdg.rdge.rdgs.ridges.rdges',
            'road'          : 'road.rd.roads.rds',
            'route'         : 'route.rte.rue.routes.rtes.rt.rts',
            'river'         : 'river.riv.rivr.rvr.rivers.rivrs.rvrs',
            'shore'         : 'shore.shr.shoar.shoars.shore.shrs',
            'spring'        : 'spring.spg.spgs.spng.spngs.springs.sprng.sprngs',
            'square'        : 'square.sq.sqr.sqre.sqrs.sqs.squ.squares',
            'street'        : 'street.st.str.stra.streets.strt.strts',
            'station'       : 'station.stn.sta.statn',
            'terrace'       : 'terrace.ter.terr.terace.trc.ters.terraces.terrs',
            'trail'         : 'trail.trl',
            'trce'          : 'trce.trce.',
            'trafficway'    : 'trafficway.trfwy.trfy.trfwys',
            'tunnel'        : 'tunnel.tnl.tunel.tunl.tunls.tunnel.tunnels.tunnl',
            'valley'        : 'valley.valley.vly.valleys.vally.vallys.vlys.vlly',
            'village'       : 'village.vill.villag.villages.ville.villg.villiage.vlg',
            'way'           : 'way.wy.wys.ways'
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

    
    def get_street_type_settings(self, *args):
        if args:
            for arg in args:
                if arg in self.street_types:
                    yield arg, self.street_type_settings[arg]
    
    def set_street_type_abbreviation(self, *args, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                if key in self.street_types:
                    if value == True or value == False:
                        self.street_type_settings[key] = value
                    else:
                        raise TypeError('Type should be boolean. ' + "'" + str(value) + "'" + ' not accepted.')
                else:
                    raise ValueError('Street type ' + "'" + str(key) + "'" + ' does not exist.')
    
    def get_all_street_type_settings(self):
        for key, value in self.street_type_settings:
            yield key, value

    def set_all_street_type_settings(self, abbrev=False):
        for key, _ in self.street_type_settings.items():
            self.street_type_settings[key] = abbrev

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
    
    def get_type_variations(self, *args):
        """Returns an iterable of street type variations for given street types."""
        for arg in args:
            if arg in self.street_types:
                yield self.street_type_converter[arg]

    def initiate_valid_address_settings(
        self, 
        AddressNumber=True, 
        StreetNamePreDirectional=False, 
        StreetNamePreType=False,
        StreetName=True, 
        StreetNamePostType=False,
        StreetNamePostDirectional=False,
        PlaceName=True,
        StateName=False,
        ZipCode=True,
        ZipCodeExtension=False
    ):
        """Set valid address settings. Can be used to change default settings."""
        self.valid_address_template = {
            'AddressNumber': AddressNumber,
            'StreetNamePreDirectional': StreetNamePreDirectional,
            'StreetNamePreType': StreetNamePreType,
            'StreetName': StreetName,
            'StreetNamePostType': StreetNamePostType,
            'StreetNamePostDirectional': StreetNamePostDirectional,
            'PlaceName': PlaceName,
            'StateName': StateName,
            'ZipCode': ZipCode,
            'ZipCodeExtension': ZipCodeExtension
        }
    
    def set_valid_address_settings(self, *args, **kwargs):
        for key, value in kwargs.items():
            if key in self.valid_address_template.keys():
                if value in (False, True):
                    self.valid_address_template[key] = value
                else:
                    raise Exception('Unknown setting ' + key + '.')

    def set_direction_type_abbreviated(self, single=False, dual=True):
        #set single
        for index, key in enumerate(list(self.direction_converter.keys())[:4]):
            self.direction_converter[key] = self.direction_names[single][index]
        #set dual
        for index, key in enumerate(list(self.direction_converter.keys())[4:]):
            self.direction_converter[key] = self.direction_names[dual][index+4]

    def standardize_direction(self, direction):
        for direction_type, standard_direction in self.direction_converter.items():
            direction_type = direction_type.split('.')
            for item in direction_type:
                if item == re.sub('[^a-zA-Z]+', '', direction).lower():
                    return standard_direction
        return None

    def dictionary_add(self, key, value):
        """Add a set of key, value to a dictionary"""
        if key not in self.parsed_dictionary.keys():
            self.parsed_dictionary[key] = value
        else:
            self.parsed_dictionary[key] += ' ' + value

    def strip_item(self, item):
        """Remove non digit, non letter characters from string."""
        return re.sub('[^0-9a-zA-Z]+', '', item)

    def reset_parser(self):
        """Reset all variables to initial values"""
        self.valid = False
        self.parsed_dictionary.clear()
        self.address = None
        self.parsed_address.clear_address()

    def parse_address(self, address):
        """Parse a single address."""
        try:
            #reset variables
            self.reset_parser()
            self.address = address

            #populate usaddress parsed dictionary
            self.parse_to_dictionary()

            #populate parsed address
            self.parsed_address.initialize_address_components(self.parsed_dictionary)

            #attempt to resolve remaining discrepancies
            self.resolve_undefined()
            self.resolve_street_name()

            #decide address validity
            self.validate_address()
        except Exception as e:
            raise Exception(str(e))

        print(self.address)
        # print(usa.parse(self.address), '\n')
        # print(self.parsed_dictionary, '\n')
        # print(self.parsed_address.get_address(), '\n')

        #get result and reset variables
        result = deepcopy(self.send_result())
        self.reset_parser()
        return result

    def get_numeric_address_number(self, AddressNumber):
        if not AddressNumber.isnumeric():
            AddressNumber = word_to_num(AddressNumber)
        return str(AddressNumber)

    def parse_to_dictionary(self):
        """Parse an address string using usaddress.parse method; populate parsed_dictionary variable."""

        #iterate through each address component
        usaddress = self.state_merge(usa.parse(self.address))
        for item in usaddress:
            #resolve AddressNumber conflicts
            if item[1] == 'AddressNumber':  
                if 'AddressNumber' not in self.parsed_dictionary.keys():
                    item[0] = re.sub('[^0-9a-zA-Z-]+', '-', item[0])
                    if '-' in item[0] and self.strip_item(item[0]).isnumeric():
                        split_item = item[0].split('-')
                        self.dictionary_add(key=self.strip_item(item[1]), value=self.get_numeric_address_number(split_item[0]))
                        for sub_item in split_item[1:]:
                            self.dictionary_add(key='AdditionalAddressNumber', value=self.strip_item(sub_item))
                    else:
                        self.dictionary_add(key=self.strip_item(item[1]), value=self.get_numeric_address_number(item[0]))
                        
                #if more than one AddressNumber, change one to UndefinedNumber
                else:
                    self.dictionary_add(key='UndefinedNumber', value=self.strip_item(item[0]))

            #building numbers
            elif item[1] == 'SubaddressIdentifier':
                if 'AddressNumber' not in self.parsed_dictionary.keys():
                    self.dictionary_add(key='AddressNumber', value=self.strip_item(item[0]))
                else:
                    self.dictionary_add(key='UndefinedNumber', value=self.strip_item(item[0]))

            #standardize predirection and postdirection to set format
            elif item[1] == 'StreetNamePreDirectional' or item[1] == 'StreetNamePostDirectional':
                self.dictionary_add(key=item[1], value=self.standardize_direction(item[0]))

            #standardize street pre-type and post-type
            elif item[1] == 'StreetNamePreType' or item[1] == 'StreetNamePostType':
                item[0] = self.standardize_street_component(component=self.decide_street_component(component=self.strip_item(item[0])))
                self.dictionary_add(key=item[1], value=item[0])

            #standardize state name to abbreviated format
            elif item[1] == 'StateName' and len(item[0])>2:
                if ',' in item[0]:
                    for split_state in item[0].split(','):
                        self.decide_undefined_state_instance(component=split_state)
                else:
                    self.decide_undefined_state_instance(component=item[0])

            #if zipcode contains extension, create two components
            elif item[1] == 'ZipCode' and '-' in item[0]:
                split_item = item[0].split('-')
                self.dictionary_add(key='ZipCode', value=self.strip_item(split_item[0]))
                self.dictionary_add(key='ZipCodeExtension', value=self.strip_item(split_item[1]))

            #if number found other than address number and zip code
            elif (item[1] != 'AddressNumber' and item[1] != 'ZipCode') and item[0].isnumeric():
                self.dictionary_add(key='UndefinedNumber', value=self.strip_item(item[0]))

            #add to dictionary as standard
            else:
                self.dictionary_add(key=self.strip_item(item[1]), value=self.strip_item(item[0]))

    def decide_undefined_state_instance(self, component):
        stripped_component = re.sub('[^a-zA-Z]+', '', component).lower()
        if stripped_component in self.state_converter.keys():
            self.dictionary_add(key='StateName', value=self.state_converter[stripped_component])
        else:
            self.dictionary_add(key='UndefinedString', value=self.strip_item(component).capitalize())  

    def resolve_undefined(self):
        """For any undefined component, try to assign its value to some component."""
        #iterate through all undefined components of all types
        for undefined_item_type in ['UndefinedNumber', 'UndefinedString']:
            if undefined_item_type in self.parsed_dictionary.keys():

                #if multiple undefined components of the same type, split
                if ' ' in self.parsed_dictionary[undefined_item_type]:
                    for undefined_split in self.parsed_dictionary[undefined_item_type].split(' '):
                        self.resolve_undefined_instance(undefined_type=undefined_item_type, undefined_component=undefined_split)

                else: self.resolve_undefined_instance(undefined_type=undefined_item_type, undefined_component=self.parsed_dictionary[undefined_item_type])

    def resolve_undefined_instance(self, undefined_type, undefined_component):
        """
        Description
        -----------
        >Assign a single undefined component to an Address component based on type.

        Parameters
        ----------
        >undefined_type -> type of undefined component
        >undefined_component -> the undefined component
        """  
        #if type is number -> use it as street name or address number
        if undefined_type == 'UndefinedNumber':
            if not self.parsed_address.get_address_component('StreetName'):
                self.parsed_address.set_address_component(component='StreetName', value=undefined_component)
            elif not self.parsed_address.get_address_component('AddressNumber'):
                self.parsed_address.set_address_component(component='AddressNumber', value=undefined_component)
        
        #if type is string and there is no city, use it as city
        elif undefined_type == 'UndefinedString':
            if not self.parsed_address.get_address_component('PlaceName'):
                self.parsed_address.set_address_component(component='PlaceName', value=undefined_component)

    #####TEMP METHOD STATE MERGE ###### UGH
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

    def check_existing_street_type(self):
        """Returns True if any street type exists in the current address, False otherwise."""
        return True if self.parsed_address.get_address_component('StreetNamePreType') or self.parsed_address.get_address_component('StreetNamePostType') else True

    def resolve_street_name(self):
        """Check for issues in street name, try to resolve if any exist."""

        function_component = 'StreetName'

        #if street name is missing -> try to get one from other components
        if not self.parsed_address.get_address_component(function_component):
            for component in self.check_components:
                if self.parsed_address.get_address_component(component):

                    #avoid using direction components if there is no existing street type component
                    if component in self.street_directions and not self.check_existing_street_type():
                        pass
                    
                    #if valid component found, switch values and break
                    else:
                        self.parsed_address.switch_components(first_component=function_component, second_component=component)
                        break
        
        #if street name is not numeric and there is a pre street type -> remove street name
        if not self.strip_item(self.parsed_address.get_address_component(component=function_component)).isnumeric() and self.parsed_address.get_address_component(component='StreetNamePreType'):
            self.parsed_address.delete_address_component(component=function_component)

        #if street name is numeric 
        if self.strip_item(self.parsed_address.get_address_component(component=function_component)).isnumeric():

            #if there is no pre-street type or pre-street type is like 'road' or 'street' -> remove street name
            if (
                not self.check_existing_street_type() 
                or ( 
                    self.parsed_address.get_address_component(component='StreetNamePreType') 
                    and self.strip_item(self.parsed_address.get_address_component(component='StreetNamePreType')).lower() in '.'.join(self.get_type_variations('road', 'street'))
                )
            ): self.parsed_address.delete_address_component(function_component)

    def validate_address(self):
        """Check whether current address is valid or not. If valid, set valid variable to True."""
        for setting, value in self.valid_address_template.items():
            if value and not self.parsed_address.get_address_component(setting):
                return #if one component missing return; self.valid remains False. 
        self.valid = True

    def send_result(self):
        """Return results of parse_address if address is valid. Raises exception if address is not valid."""
        if self.valid:
            return self.parsed_address
        raise Exception('Invalidd address.')

