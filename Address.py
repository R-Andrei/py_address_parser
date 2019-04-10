class Address:
    """
    Description
    -----------
    >A Class used to represent an address. Contains multiple components.

    Paramaters
    ----------
    >parsed_address - dictionary containing address components and values

    Components
    ----------
    
    >AddressNumber -> address number of address (e.g. >751< West Howell Street)

    >AdditionalAddressNumber -> additional address number, is not displayed, only recorded
    
    >StreetNamePreDirectional -> direction before street name (e.g. 551 >West< Howell Street)
   
    >StreetNamePreType -> type before street name (e.g. 12 East >Highway< 51 North)
    
    >StreetName -> name of the street (e.g. 751 West >Howell< Street)
    
    >StreetNamePostType -> type after street name (e.g. 751 West Howell >Street<)
    
    >StreetNamePostDirectional -> direction after street name (e.g. 12 East Highway 51 >North<)
    
    >Place Name -> name of the city (e.g. 21 Michigan Avenue, >Campbell<, NC 75121-1234)
    
    >StateName -> name of the state (e.g. 21 Michigan Avenue, Campbell, >NC< 75121-1234)
    
    >ZipCode -> zipcode base (e.g. 21 Michigan Avenue, Campbell, NC >75121<-1234)
    
    >ZipCodeExtension -> extension of zip-code (e.g. 21 Michigan Avenue, Campbell, NC 75121->1234<)

    Usable methods
    --------------
    >get_address() -> returns the main storage variable containing all components and their values

    >get_address_component(component) -> returns the value of the given component

    >set_address_component(component, value) -> sets the given address component to the given value

    >delete_address_component(component) -> removes the value for the given address component

    >switch_components(first_component, second_component) -> switches the values of the given components

    >get_all_values() -> returns an iterable of all current existing values

    >unpack() -> returns the address as a string
    
    """
    def __init__(self, parsed_address):

        #Initialize the address as empty
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
        
        #Set values equal to given values from parameter
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
        """
        Description
        -----------
        >Returns the first existing component after a given position. 

        Parameters
        ----------
        >index -> an integer indicating the current position

        Output
        ------
        >component name if next occuring component value exists else None
        """
        for component_index in range(index + 1, len(self.__address)):
            if self.__address[self.keys[component_index]]:
                return self.keys[component_index]
        return None
    
    def initialize_address_components(self, parsed_address):
        """
        Description
        -----------
        >Method used at the initialization of the object instance. Calling this is not recommended,
        unless reusing the same instance for multiple addresses. 

        Parameters
        ----------
        >parsed_address -> dictionary containing keys and values for address components
        """
        for component, value in parsed_address.items():
            if component in self.__address.keys():
                if value:
                    self.__address[component] = value

    def get_address(self):
        """Returns the main storage variable."""
        return self.__address

    def get_address_component(self, component):
        """Returns a component based on input."""
        return self.__address[component] if component in self.__address.keys() else None

    def set_address_component(self, component, value):
        """Sets the value for a given component based on input."""
        if component in self.__address.keys():
            self.__address[component] = value if value else ''
    
    def delete_address_component(self, component):
        """Removes the value for a given component."""
        if component in self.__address.keys():
            self.__address[component] = ''
             
    def switch_components(self, first_component, second_component):
        """Switches the values of two given components."""
        self.__address[first_component], self.__address[second_component] = self.__address[second_component], self.__address[first_component]

    def clear_address(self):
        """Removes all values for all components."""
        for component in self.__address.keys():
            self.__address[component] = ''
    
    def get_all_values(self):
        """Returns an iterable of all existing values."""
        return (value for value in self.__address.values() if value)

    def unpack(self):
        """Returns the address as a string."""
        return self.__repr__()
