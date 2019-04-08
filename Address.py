class Address:
    def __init__(self, parsed_address):
        self.__address = {
            'AddressNumber': '',
            'AdditionalAddressNumber': '',
            'StreetNamePreDirectional': '',
            'StreetNamePreType': '',
            'StreetName': '',
            'StreetNamePostType': '',
            'StreetNamePostDirectional': '',
            'PlaceName': '',
            'StateName': '',
            'ZipCode': '',
            'ZipCodeExtension': ''
        }
        self.initialize_address_components(parsed_address)
        self.keys = list(self.__address.keys())
    
    def __eq__(self, other):
        return tuple(self.get_all_values()) == tuple(other.get_all_values())
    
    def __repr__(self):
        returnstring = ''
        for index, _ in enumerate(self.__address.keys()):
            if self.__address[self.keys[index]]:
                if self.keys[index] != 'AdditionalAddressNumber':
                    returnstring += self.__address[self.keys[index]]
                    if self.next_component(index) in ['PlaceName', 'StateName']:
                        returnstring += ', '
                    elif self.next_component(index) == 'ZipCodeExtension':
                        returnstring += '-'
                    else:
                        returnstring += ' '
        return returnstring

    def next_component(self, index):
        for component_index in range(index + 1, len(self.__address)):
            if self.__address[self.keys[component_index]]:
                return self.keys[component_index]
        return None
    
    def initialize_address_components(self, parsed_address):
        for component, value in parsed_address.items():
            if component in self.__address.keys():
                if value:
                    self.__address[component] = value

    def get_address(self):
        return self.__address

    def get_address_component(self, component):
        if component in self.__address.keys():
            return self.__address[component]

    def set_address_component(self, component, value):
        if component in self.__address.keys():
            if value:
                self.__address[component] = value
            else: 
                self.__address[component] = ''
    
    def delete_address_component(self, component):
        if component in self.__address.keys():
            self.__address[component] = ''
                
    def switch_components(self, first_component, second_component):
        self.__address[first_component], self.__address[second_component] = self.__address[second_component], self.__address[first_component]

    def clear_address(self):
        for component in self.__address.keys():
            self.__address[component] = ''
    
    def get_all_values(self):
        return self.__address.values()

    def unpack(self):
        return self.__repr__()