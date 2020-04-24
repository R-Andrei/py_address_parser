
from copy import deepcopy
import re

import usaddress as usa

from .address_components import address_components
from .address import Address
from .component import AddressComponent
from .componentcontainer import ComponentContainer
from .converter import to_digits


class Parser:
    """
    Usage of Parser class:

    - define parser object like 'parser = Parser()'
    - optionally define settings, using methods: set_valid_address_settings, set_street_type_settings, set_all_street_type_settings, set_direction_type_settings
    - call 'parse' method, assign result to a variable like 'my_address = parser.parse(address)'

    > ! Parser returns Address type objects.


    Methods
    -------

    > parse [main method]:
        > Parses an address (using current configuration) and returns an [Address] object containing components from the given address.
        > parameters: 
            > address [str] [required] -> string that contains an address to be parsed
        > output:
            > [Address object] -> dict-like object containing recognized components from parsed-address


    > set_valid_address_settings [setting method]:
        > Sets which address components are required for an address to be valid. By default no components are required.
        > parameters:
            > AddressNumber [keyword] [boolean] [optional]
            > StreetNamePreType [keyword] [boolean] [optional]
            > StreetNamePostType [keyword] [boolean] [optional]
            > PlaceName [keyword] [boolean] [optional]
            > ZipCode [keyword] [boolean] [optional]
            > StreetNamePreDirectional [keyword] [boolean] [optional]
            > StreetName [keyword] [boolean] [optional]
            > StreetNamePostDirectional [keyword] [boolean] [optional]
            > StateName [keyword] [boolean] [optional]
            > ZipCodeExtension [keyword] [boolean] [optional]
        > output:
            > None


    > set_direction_type_settings [setting method]:
        > Sets which types of directions (singular/dual) should be abbreviated. By default dual directions are abbreviated. (E.g. Northeast -> NE)
        > parameters:
            > single [keyword] [boolean] [default=False]
            > dual [keyword] [boolean] [default=True]
        > output:
            > None


    > set_all_street_type_settings [setting method]:
        > Sets whether all street types should be abbreviated. By default no street types are abbreviated.
        > parameters:
            > abbreviate [keyword] [boolean] [default=False]
        output:
            > None


    > set_street_type_settings [setting method]:
        > Sets which street types should be abbreviated. By default no street type is abbreviated.
        > parameters:
            > alley [keyword] [boolean] [optional]
            > annex [keyword] [boolean] [optional]
            > arcade [keyword] [boolean] [optional]
            > avenue [keyword] [boolean] [optional]
            > bluff [keyword] [boolean] [optional]
            > bottom [keyword] [boolean] [optional]
            > boulevard [keyword] [boolean] [optional]
            > branch [keyword] [boolean] [optional]
            > bridge [keyword] [boolean] [optional]
            > bypass [keyword] [boolean] [optional]
            > causeway [keyword] [boolean] [optional]
            > center [keyword] [boolean] [optional]
            > circle [keyword] [boolean] [optional]
            > cliff [keyword] [boolean] [optional]
            > court [keyword] [boolean] [optional]
            > cove [keyword] [boolean] [optional]
            > crescent [keyword] [boolean] [optional]
            > curve [keyword] [boolean] [optional]
            > drive [keyword] [boolean] [optional]
            > estate [keyword] [boolean] [optional]
            > expressway [keyword] [boolean] [optional]
            > extension [keyword] [boolean] [optional]
            > fork [keyword] [boolean] [optional]
            > freeway [keyword] [boolean] [optional]
            > garden [keyword] [boolean] [optional]
            > gateway [keyword] [boolean] [optional]
            > grove [keyword] [boolean] [optional]
            > harbor [keyword] [boolean] [optional]
            > highway [keyword] [boolean] [optional]
            > hill [keyword] [boolean] [optional]
            > hollow [keyword] [boolean] [optional]
            > island [keyword] [boolean] [optional]
            > isle [keyword] [boolean] [optional]
            > junction [keyword] [boolean] [optional]
            > key [keyword] [boolean] [optional]
            > landing [keyword] [boolean] [optional]
            > lane [keyword] [boolean] [optional]
            > loop [keyword] [boolean] [optional]
            > meadow [keyword] [boolean] [optional]
            > mhp [keyword] [boolean] [optional]
            > mill [keyword] [boolean] [optional]
            > mountain [keyword] [boolean] [optional]
            > park [keyword] [boolean] [optional]
            > parkway [keyword] [boolean] [optional]
            > passage [keyword] [boolean] [optional]
            > turnpike [keyword] [boolean] [optional]
            > place [keyword] [boolean] [optional]
            > plain [keyword] [boolean] [optional]
            > plz [keyword] [boolean] [optional]
            > point [keyword] [boolean] [optional]
            > port [keyword] [boolean] [optional]
            > radial [keyword] [boolean] [optional]
            > ranch [keyword] [boolean] [optional]
            > ridge [keyword] [boolean] [optional]
            > road [keyword] [boolean] [optional]
            > route [keyword] [boolean] [optional]
            > river [keyword] [boolean] [optional]
            > shore [keyword] [boolean] [optional]
            > spring [keyword] [boolean] [optional]
            > square [keyword] [boolean] [optional]
            > street [keyword] [boolean] [optional]
            > station [keyword] [boolean] [optional]
            > terrace [keyword] [boolean] [optional]
            > trail [keyword] [boolean] [optional]
            > trce [keyword] [boolean] [optional]
            > trafficway [keyword] [boolean] [optional]
            > tunnel [keyword] [boolean] [optional]
            > valley [keyword] [boolean] [optional]
            > village [keyword] [boolean] [optional]
            > way [keyword] [boolean] [optional]
    """

    def __init__(self, *args, **kwargs):

        # address storage
        self.__address = None
        self.__saddress_components = ComponentContainer()
        self.__parsed_address = Address()

        # valid address settings
        self.__valid_address_template = {component: False for component in address_components}
        self.__valid = self.__validate_address()

        # components to be checked frequently
        self.__check_components = ('StreetNamePostType', 'StreetNamePreType',
                                   'StreetNamePreDirectional', 'StreetNamePostDirectional')
        self.__street_directions = self.__check_components[2:]

        # state conversion
        self.__state_converter = {
            'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
            'california': 'CA', 'georgia': 'GA', 'iowa': 'IA', 'maryland': 'MD',
            'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE', 'florida': 'FL',
            'hawaii': 'HI', 'idaho': 'ID', 'illinois': 'IL', 'indiana': 'IN',
            'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME',
            'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
            'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
            'newjersey': 'NJ', 'newmexico': 'NM', 'newyork': 'NY', 'northcarolina': 'NC',
            'northdakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR',
            'rhodeisland': 'RI', 'southcarolina': 'SC', 'southdakota': 'SD', 'tennessee': 'TN',
            'texas': 'TX', 'utah': 'UT', 'vermont': 'VT', 'virginia': 'VA',
            'washington': 'WA', 'westvirginia': 'WV', 'wisconsin': 'WI', 'wyoming': 'WY',
            'newhampshire': 'NH', 'pennsylvania': 'PA', 'puertorico': 'PR'
        }

        # direction conversion
        self.__direction_names = {
            True:   ['N',       'E',      'S',       'W',      'NE',          'NW',          'SE',          'SW'],
            False:  ['North',   'East',   'South',   'West',   'Northeast',   'Northwest',   'Southeast',   'Southwest']
        }

        self.__direction_converter = {
            'north.n': None,
            'east.e': None,
            'south.s': None,
            'west.w': None,
            'northeast.ne': None,
            'northwest.nw': None,
            'southeast.se': None,
            'southwest.sw': None
        }
        self.set_direction_type_settings()

        # street type conversion
        self.__street_type_converter = {
            'alley': 'alley.aly.allee.ally',                    'annex': 'annex.anx.anex.annx',
            'arcade': 'arcade.arc.arcades.arcs',                'avenue': 'avenue.ave.av.aven.avenu.avn.avnue',
            'bluff': 'bluff.blf.blfs.bluf.bluffs',              'bottom': 'bottom.bot.bottm.btm',
            'boulevard': 'boulevard.blvd.boulv.boul',           'branch': 'branch.br.brnch',
            'bridge': 'bridge.brg.brdge',                       'bypass': 'bypass.byps.byp.bypa.bypas',
            'causeway': 'causeway.cswy.causwa.causewy.csway',   'center': 'center.cen.cent.centers.centr.centre.cnter.cntr.ctr',
            'cliff': 'cliff.clf.clfs.cliffs',                   'circle': 'circle.cir.circ.circl.circles.cirs.crcl.crcle',
            'court': 'court.ct.courts.crt.cts',                 'cove': 'cove.cv.cve.coves',
            'curve': 'curve.cv.curv.cvs',                       'crescent': 'crescent.cres.crest.crse.crsent.crsnt.crst',
            'drive': 'drive.dr.driv.drives.drs.drv.dv',         'estate': 'estate.est.estates.ests',
            'fork': 'fork.frk.forks.frks',                      'expressway': 'expressway.expwy.exp.expr.express.expw.expy',
            'freeway': 'freeway.fwy.freewy.frway.frwy.fry',     'extension': 'extension.ext.extensions.extn.extnsn.exts',
            'gateway': 'gateway.gtwy.gatewy.gatway.gtway',      'garden': 'garden.gdn.gardens.gardn.gdns.grden.grdn.grdns',
            'grove': 'grove.grv.grov.groves.grvs',              'harbor': 'harbor.hbr.harb.harbors.harbr.hbrs.hrbor.hrbr',
            'hill': 'hill.hl.hills.hls',                        'hollow': 'hollow.hlw.hollows.holw.holws.hllw.holw.holws',
            'island': 'island.islnd.island.islnds.iss',         'isle': 'isle.is.isles.',
            'key': 'key.key.keys.ky.kys',                       'junction': 'junction.jctn.jct.jctns.jcts.junctions.junctn.juncton',
            'landing': 'landing.land.lndg.lndng',               'lane': 'lane.ln.lne.lanes.lnes.lns.lans',
            'loop': 'loop.loop.loops',                          'meadow': 'meadow.mdw.mdws.meadows.medows',
            'mhp': 'mhp.mhp',                                   'mill': 'mill.ml.mills.mls.mils',
            'park': 'park.park.parks.prks.prk',                 'mountain': 'mountain.mt.mount.mountains.mountin.mtin.mtn.mtns.mtwy',
            'place': 'place.pl.pls.places',                     'parkway': 'parkway.pkwy.parkways.parkwy.pkway.pkwys.pky',
            'plain': 'plain.pln.plains.plns',                   'turnpike': 'turnpike.tpke.pike.turnpk.pikes.pke.pkes',
            'plz': 'plz.plz',                                   'passage': 'passage.pass.passages.psg.psgs.psge',
            'port': 'port.prt.ports.prts',                      'point': 'point.pt.pointe.points.pointes.ptes.pts',
            'radial': 'radial.rad.radiel.radl',                 'ranch': 'ranch.rnch.ranches.rnchs',
            'ridge': 'ridge.rdg.rdge.rdgs.ridges.rdges',        'road': 'road.rd.roads.rds',
            'route': 'route.rte.rue.routes.rtes.rt.rts',        'river': 'river.riv.rivr.rvr.rivers.rivrs.rvrs',
            'shore': 'shore.shr.shoar.shoars.shore.shrs',       'spring': 'spring.spg.spgs.spng.spngs.springs.sprng.sprngs',
            'station': 'station.stn.sta.statn',                 'square': 'square.sq.sqr.sqre.sqrs.sqs.squ.squares',
            'trail': 'trail.trl',                               'street': 'street.st.str.stra.streets.strt.strts',
            'trafficway': 'trafficway.trfwy.trfy.trfwys',       'terrace': 'terrace.ter.terr.terace.trc.ters.terraces.terrs',
            'way': 'way.wy.wys.ways',                           'tunnel': 'tunnel.tnl.tunel.tunl.tunls.tunnel.tunnels.tunnl',
            'valley': 'valley.valley.vly.valleys.vally.vallys.vlys.vlly',
            'village': 'village.vill.villag.villages.ville.villg.villiage.vlg',
            'highway': 'highway.hwy.highwy.hiway.hiwy.hway.motorway.motorwy.mtrway.throughway.thruway.thruways.thrwy'
        }

        self.__street_type_settings = {
            'alley': False,         'annex': False,     'arcade': False,    'avenue': False,    'bluff': False,
            'bottom': False,        'boulevard': False, 'branch': False,    'bridge': False,    'bypass': False,
            'causeway': False,      'center': False,    'circle': False,    'cliff': False,     'court': False,
            'cove': False,          'crescent': False,  'curve': False,     'drive': False,     'estate': False,
            'expressway': False,    'extension': False, 'fork': False,      'freeway': False,   'garden': False,
            'gateway': False,       'grove': False,     'harbor': False,    'highway': False,   'hill': False,
            'hollow': False,        'island': False,    'isle': False,      'junction': False,  'key': False,
            'landing': False,       'lane': False,      'loop': False,      'meadow': False,    'mhp': False,
            'mill': False,          'mountain': False,  'park': False,      'parkway': False,   'passage': False,
            'turnpike': False,      'place': False,     'plain': False,     'plz': False,       'point': False,
            'port': False,          'radial': False,    'ranch': False,     'ridge': False,     'road': False,
            'route': False,         'river': False,     'shore': False,     'spring': False,    'square': False,
            'street': False,        'station': False,   'terrace': False,   'trail': False,     'trafficway': False,
            'tunnel': False,        'valley': False,    'village': False,   'way': False
        }

        self.__street_types = tuple(self.__street_type_settings.keys())

    def parse(self, address):
        """Parse a single address."""
        self.__reset_parser()
        try:
            # store new address
            self.__address = address

            # populate usaddress component container
            self.__parse_to_component_container()

            # create parsed address using parsed components
            self.__parsed_address.initialize_address(
                self.__saddress_components)

            # attempt to resolve remaining inconsistencies
            self.__resolve_undefined()
            self.__resolve_street_name()
            self.__resolve_address_number()

            # decide address validity
            self.__valid = self.__validate_address()
        except Exception as e:
            self.__reset_parser()
            raise Exception(str(e))

        # get result and reset variables
        result = deepcopy(self.__send_result())
        self.__reset_parser()
        return result

    # Address validity settings
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
        for key, value in kwargs.items():  # NOT DONE
            if key in self.__parsed_address.keys:  # NOT DONE
                if type(value) == bool:  # NOTDONE
                    self.__valid_address_template[key] = value  # NOTDONE
                else:
                    raise TypeError(
                        'Value of ' + key + ' is incorrect, must be either True or False, not ' + str(value))
            else:
                invalid_container.append(key)

        if invalid_container:
            raise Exception('Invalid settings:', str(invalid_container))
    # Street type settings

    def get_street_type_settings(self, *args):
        for arg in args:
            if arg in self.__street_types:
                yield arg, self.__street_type_settings[arg]

    def set_street_type_settings(self, *args, **kwargs):
        for key, value in kwargs.items():
            if key in self.__street_types:
                if type(value) == bool:
                    self.__street_type_settings[key] = value
                else:
                    raise TypeError('Type should be boolean. ' +
                                    "'" + str(value) + "'" + ' not accepted.')
            else:
                raise ValueError('Street type ' + "'" +
                                 str(key) + "'" + ' does not exist.')

    def get_all_street_type_settings(self):
        for key, value in self.__street_type_settings.items():
            yield key, value

    def set_all_street_type_settings(self, abbreviate=False):
        for key, _ in self.__street_type_settings.items():
            self.__street_type_settings[key] = abbreviate
    # START street direction settings

    def set_direction_type_settings(self, single=False, dual=True):
        # set single
        for index, key in enumerate(list(self.__direction_converter.keys())[:4]):
            self.__direction_converter[key] = self.__direction_names[single][index]
        # set dual
        for index, key in enumerate(list(self.__direction_converter.keys())[4:]):
            self.__direction_converter[key] = self.__direction_names[dual][index+4]

    def get_type_variations(self, *args):
        """Returns an iterable of street type variations for given street types."""
        for arg in args:
            if arg in self.__street_types:
                yield self.__street_type_converter[arg]

    def standardize_direction(self, direction):
        for direction_type, standard_direction in self.__direction_converter.items():
            direction_type = direction_type.split('.')
            for item in direction_type:
                if item == re.sub('[^a-zA-Z]+', '', direction).lower():
                    return standard_direction
        return None

    def check_existing_street_type(self):
        """Returns True if any street type exists in the current address, False otherwise."""
        return True if self.__parsed_address['StreetNamePreType'] or self.__parsed_address['StreetNamePostType'] else True

    # METHODS THAT SHOULD NOT BE CALLED AT ALL
    def __resolve_street_name(self):
        """
        Description
        -----------
        >Checks for issues in street name, tries to resolve if any exist.
        """

        function_component = 'StreetName'

        # if street name is missing -> try to get one from other components
        if not self.__parsed_address[function_component]:
            for component in self.__check_components:
                if self.__parsed_address[component]:

                    # avoid using direction components if there is no existing street type component
                    if component in self.__street_directions and not self.check_existing_street_type():
                        pass

                    # if valid component found, switch values and break
                    else:
                        self.__parsed_address.switch_components(
                            first_component=function_component, second_component=component)
                        break

        # if street name is numeric
        if self.__strip_item(self.__parsed_address[function_component].value).isnumeric():

            # if there is no pre-street type or pre-street type is like 'road' or 'street' -> remove street name
            if (
                not self.check_existing_street_type()
                or (
                    self.__parsed_address['StreetNamePreType']
                    and self.__strip_item(self.__parsed_address['StreetNamePreType'].value).lower() in '.'.join(self.get_type_variations('road', 'street'))
                )
            ):
                self.__parsed_address.clear_address_component(
                    function_component)

    def __resolve_address_number(self):
        # if state is NY check for composed address number
        if self.__parsed_address['AdditionalAddressNumber'].exists() and self.__parsed_address['StateName'].value == 'NY':
            self.__parsed_address['AddressNumber'] = '{AddressNumber}-{AdditionalAddressNumber}'\
                .format(
                    AddressNumber=self.__parsed_address['AddressNumber'].value,
                    AdditionalAddressNumber=self.__parsed_address['AdditionalAddressNumber'].value
            )
            self.__parsed_address.clear_address_component(
                'AdditionalAddressNumber')

        # if address number does not contain digits remove
        if re.sub(r'\D', '', self.__parsed_address['AddressNumber'].value) < re.sub(r'\d', '', self.__parsed_address['AddressNumber'].value):
            self.__parsed_address.clear_address_component('AddressNumber')

    def __check_hyphen_name(self, item1, item2):
        if item1.isnumeric() and (item2.upper() in tuple(self.__state_converter.values()) or item2.lower() == 'us'):
            return '{item2}-{item1}'.format(item1=item1, item2=item2)
        return None

    def __parse_to_component_container(self):

        # iterate through each address component
        usaddress = self.__state_merge(usa.parse(self.__address))
        for item in usaddress:
            # resolve AddressNumber conflicts
            if item[1] == 'AddressNumber':
                if 'AddressNumber' not in self.__saddress_components:
                    item[0] = re.sub('[^0-9a-zA-Z-]+', '-', item[0])
                    if '-' in item[0] and self.__strip_item(item[0]).isnumeric():
                        component_values = item[0].split('-')
                        self.__append_address_components(
                            AddressComponent(item[1], self.__get_numeric_address_number(component_values[0])))
                        for sub_component in component_values[1:]:
                            self.__append_address_components(
                                AddressComponent('AdditionalAddressNumber', self.__strip_item(sub_component)))
                    else:
                        self.__append_address_components(
                            AddressComponent(item[1], self.__get_numeric_address_number(item[0])))
                # if more than one AddressNumber, change one to UndefinedNumber
                else:
                    self.__append_address_components(
                        AddressComponent('UndefinedNumber', self.__strip_item(item[0])))

            # street name capitalization and character stripping
            elif item[1] == 'StreetName':
                if '-' in item[0]:
                    split_item = item[0].split('-')
                    if len(split_item) == 2:
                        component_item = self.__check_hyphen_name(item1=self.__strip_item(
                            split_item[0]), item2=self.__strip_item(split_item[1]))
                        component_item = component_item if component_item else self.__check_hyphen_name(
                            item1=self.__strip_item(split_item[1]),
                            item2=self.__strip_item(split_item[0])
                        )
                        if component_item:
                            self.__append_address_components(
                                AddressComponent(self.__strip_item(item[1]), component_item))
                        else:
                            self.__append_address_components(
                                AddressComponent(self.__strip_item(item[1]), self.__strip_item(item[0]).capitalize()))
                    else:
                        self.__append_address_components(AddressComponent(self.__strip_item(
                            item[1]), self.__strip_item(split_item[0]).capitalize()))
                else:
                    self.__append_address_components(
                        AddressComponent(self.__strip_item(item[1]), self.__strip_item(item[0]).capitalize()))
            # building numbers
            elif item[1] == 'SubaddressIdentifier':
                if 'AddressNumber' not in self.__saddress_components:
                    self.__append_address_components(
                        AddressComponent('AddressNumber', self.__get_numeric_address_number(item[0])))
                else:
                    self.__append_address_components(
                        AddressComponent('UndefinedNumber', self.__strip_item(item[0])))

            # standardize predirection and postdirection
            elif item[1] == 'StreetNamePreDirectional' or item[1] == 'StreetNamePostDirectional':
                self.__append_address_components(
                    AddressComponent(item[1], self.standardize_direction(item[0])))

            # standardize street types
            elif item[1] == 'StreetNamePreType' or item[1] == 'StreetNamePostType':
                item[0] = self.__standardize_street_component(
                    component=self.__decide_street_component(component=self.__strip_item(item[0])))
                self.__append_address_components(
                    AddressComponent(item[1], item[0]))

            # standardize state name to abbreviated format
            elif item[1] == 'StateName' and len(item[0]) > 2:
                if ',' in item[0]:
                    for split_state in item[0].split(','):
                        self.__parse_state_component(component=split_state)
                else:
                    self.__parse_state_component(component=item[0])

            # if zipcode contains extension, create two components
            elif item[1] == 'ZipCode' and '-' in item[0]:
                split_item = item[0].split('-')
                self.__append_address_components(
                    AddressComponent('ZipCode', self.__strip_item(split_item[0])))
                self.__append_address_components(
                    AddressComponent('ZipCodeExtension', self.__strip_item(split_item[1])))

            # if number found other than AddressNumber or ZipCode
            elif (item[1] != 'AddressNumber' and item[1] != 'ZipCode') and item[0].isnumeric():
                self.__append_address_components(
                    AddressComponent('UndefinedNumber', self.__strip_item(item[0])))

            # add to dictionary as standard
            else:
                self.__append_address_components(
                    AddressComponent(self.__strip_item(item[1]), self.__strip_item(item[0])))

    def __parse_state_component(self, component):
        """
        Description
        -----------
        >Adds a component to the parsed_dictionary based on whether it's a state or not.

        Parameters
        ----------
        >component -> value of a component, if state-like, then add as a state component, otherwise as undefined
        """
        stripped_component = re.sub('[^a-zA-Z]+', '', component).lower()
        if stripped_component in self.__state_converter.keys():
            self.__append_address_components(AddressComponent(
                component_name='StateName', component_value=self.__state_converter[stripped_component]))
        else:
            self.__append_address_components(AddressComponent(
                component_name='UndefinedString', component_value=self.__strip_item(component).capitalize()))

    def __resolve_undefined(self):
        """
        Description
        -----------
        >Iterate through existing undefined components, call self.__resolve_undefined_instance for each separate component.
        """
        # iterate through all undefined components of all types
        for undefined_item_type in ['UndefinedNumber', 'UndefinedString']:
            if undefined_item_type in self.__saddress_components:
                # if multiple undefined components of the same type, split
                if ' ' in self.__saddress_components[undefined_item_type].value:
                    for undefined_split in self.__saddress_components[undefined_item_type].value.split(' '):
                        self.__resolve_undefined_instance(
                            undefined_type=undefined_item_type, undefined_component=undefined_split)

                else:
                    self.__resolve_undefined_instance(
                        undefined_type=undefined_item_type, undefined_component=self.__saddress_components[undefined_item_type].value)

    def __resolve_undefined_instance(self, undefined_type, undefined_component):
        """
        Description
        -----------
        >Assign a single undefined component to another component based on type.

        Parameters
        ----------
        >undefined_type -> type of undefined component

        >undefined_component -> the undefined component
        """
        # if type is number -> use it as street name or address number
        if undefined_type == 'UndefinedNumber':
            if not self.__parsed_address['StreetName']:
                self.__parsed_address['StreetName'] = undefined_component
            elif not self.__parsed_address['AddressNumber']:
                self.__parsed_address['AddressNumber'] = undefined_component

        # if type is string and there is no city, use it as city
        elif undefined_type == 'UndefinedString':
            if not self.__parsed_address['PlaceName']:
                self.__parsed_address['PlaceName'] = undefined_component
    # TODO: create better method

    def __state_merge(self, usaddress_list):
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

        # change immutable sub-sets to mutables
        for index in range(len(usaddress_list)):
            usaddress_list[index] = list(usaddress_list[index])

        # merge state names if multiple
        for index, item in enumerate(usaddress_list):
            if item[1] == 'StateName' and found == False:
                found, position = True, index
            elif item[1] == 'StateName' and found == True:
                usaddress_list[position][0] += ' ' + item[0]
                del usaddress_list[index]
                position = index

        return tuple(usaddress_list)

    # PARSE ADDRESS MAIN LOOP
    def __reset_parser(self):
        """Reset all variables to initial values"""
        self.__saddress_components.clear()
        self.__address = None
        self.__parsed_address.clear_address()
        self.__valid = self.__validate_address()

    def __validate_address(self):
        """Check whether current address is valid or not. If valid, set valid variable to True."""
        for setting, value in self.__valid_address_template.items():
            if value and not self.__parsed_address[setting].value:
                # if one component missing return; self.__valid remains False.
                return False
        return True

    def __send_result(self):
        """Return results of parse if address is valid. Raises exception if address is not valid."""
        if self.__valid:
            return self.__parsed_address
        raise Exception('Invalidd address.')

    def __append_address_components(self, component):
        if not self.__saddress_components.has_component(component):
            self.__saddress_components[component.name] = component
        else:
            self.__saddress_components[component.name].value += ' ' + \
                component.value

    # Street type standardization
    def __standardize_street_component(self, component):
        if component in self.__street_types:
            if self.__street_type_settings[component]:
                return self.__street_type_converter[component].split('.')[1].capitalize()
            return self.__street_type_converter[component].split('.')[0].capitalize()
        else:
            return component.capitalize()

    def __decide_street_component(self, component):
        for key, value in self.__street_type_converter.items():
            component_types = value.split('.')
            for component_type in component_types:
                if component_type == component.lower():
                    return key
        return component

    # UTILITY METHODS
    def __strip_item(self, item):
        """Remove non digit, non letter characters from string."""
        return re.sub('[^0-9a-zA-Z]+', '', item)

    def __get_numeric_address_number(self, AddressNumber):
        """Return numeric representation of number if number is initially a word."""
        return str(to_digits(AddressNumber)) if not AddressNumber.isnumeric() else AddressNumber
