import re
import usaddress as usa
from Address import Address
from copy import deepcopy

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
            self.resolve_remaining_conflicts()

            #decide address validity
            self.validate_address()
        except Exception as e:
            raise Exception(str(e))

        print(self.address)
        # print(self.parsed_dictionary, '\n')
        # print(self.parsed_address.get_address(), '\n')
        # print(usa.parse(self.address), '\n')

        #get result and reset variables
        result = deepcopy(self.send_result())
        self.reset_parser()
        return result

    def parse_to_dictionary(self):
        """Parse an address string using usaddress.parse method; populate parsed_dictionary variable."""

        #iterate through each address component
        usaddress = self.state_merge(usa.parse(self.address))
        for item in usaddress:

            #resolve AddressNumber conflicts
            if item[1] == 'AddressNumber':  
                if 'AddressNumber' not in self.parsed_dictionary.keys():
                    if '-' in item[0] and self.strip_item(item[0]).isnumeric():
                        split_item = item[0].split('-')
                        self.dictionary_add(key=self.strip_item(item[1]), value=split_item[0])
                        for sub_item in split_item[1:]:
                            self.dictionary_add(key='AdditionalAddressNumber', value=self.strip_item(sub_item))
                    else:
                        self.dictionary_add(key=self.strip_item(item[1]), value=self.strip_item(item[0]))

                #if more than one AddressNumber, change one to UndefinedNumber
                else:
                    self.dictionary_add(key='UndefinedNumber', value=self.strip_item(item[0]))

            #standardize predirection and postdirection to set format
            elif item[1] == 'StreetNamePreDirectional' or item[1] == 'StreetNamePostDirectional':
                self.dictionary_add(key=item[1], value=self.standardize_direction(item[0]))

            #standardize state name to abbreviated format
            elif item[1] == 'StateName' and len(item[1])>2:
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

    def resolve_remaining_conflicts(self):
        """Attempt to resolve undefined numbers and lack of street name issues."""
        self.resolve_undefined()
        self.resolve_street_name()

    def resolve_undefined(self):
        """Check for any undefined components and try to assign to missing Address components."""
        #resolve undefined numbers
        for undefined_item_type in ['UndefinedNumber', 'UndefinedString']:
            if undefined_item_type in self.parsed_dictionary.keys():
                if ' ' in self.parsed_dictionary[undefined_item_type]:
                    for undefined_split in self.parsed_dictionary[undefined_item_type].split(' '):
                        self.resolve_undefined_instance(undefined_type=undefined_item_type, undefined_component=undefined_split)
                else: 
                    self.resolve_undefined_instance(undefined_type=undefined_item_type, undefined_component=self.parsed_dictionary[undefined_item_type])

    def resolve_undefined_instance(self, undefined_type, undefined_component):
        """Assign an undefined component to an Address component."""  
        if undefined_type == 'UndefinedNumber':
            if not self.parsed_address.get_address_component('StreetName'):
                self.parsed_address.set_address_component(component='StreetName', value=undefined_component)
            elif not self.parsed_address.get_address_component('AddressNumber'):
                self.parsed_address.set_address_component(component='AddressNumber', value=undefined_component)
        elif undefined_type == 'UndefinedString':
            if not self.parsed_address.get_address_component('PlaceName'):
                self.parsed_address.set_address_component(component='PlaceName', value=undefined_component)

    #####TEMP METHOD STATE MERGE ###### UGH
    def state_merge(self, usaddress_list):
        """Iterate through output of usaddress.parse, change immutables to mutable and merge where multiple."""
        found, position = False, None
        for index in range(len(usaddress_list)):
            usaddress_list[index] = list(usaddress_list[index])
        for index, item in enumerate(usaddress_list):
            if item[1] == 'StateName' and found == False:
                found, position = True, index
            elif item[1] == 'StateName' and found == True:
                usaddress_list[position][0] += ' ' + item[0]
                del usaddress_list[index]
                position = index
        return usaddress_list

    def resolve_street_name(self):
        """Check if street name missing, try to get a valid street name from other components."""
        function_component = 'StreetName'
        check_components = ['StreetNamePostType', 'StreetNamePreType', 'StreetNamePreDirectional', 'StreetNamePostDirectional']

        #if street name is missing, try to get one from other components
        if not self.parsed_address.get_address_component(function_component):
            for component in check_components:
                if self.parsed_address.get_address_component(component):
                    self.parsed_address.switch_components(first_component=function_component, second_component=component)
                    break
        
        #if street name is not numeric and there is a pre street type, remove street name
        if not self.strip_item(self.parsed_address.get_address_component(function_component)).isnumeric() and self.parsed_address.get_address_component('StreetNamePreType'):
            self.parsed_address.delete_address_component(function_component)


    def validate_address(self):
        """Check whether current address is valid or not. If valid, set valid variable to True."""
        for setting, value in self.valid_address_template.items():
            if value and not self.parsed_address.get_address_component(setting):
                return
        self.valid = True

    def send_result(self):
        """Return results of parse_address based on address validity"""
        if self.valid:
            return self.parsed_address
        raise Exception('Invalidd address.')
