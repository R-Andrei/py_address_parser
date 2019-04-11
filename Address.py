from AddressContainer import AddressContainer
from Component import Component

class Address(object):
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

    >clear_address_component(component) -> removes the value for the given address component

    >switch_components(first_component, second_component) -> switches the values of the given components

    >get_all_values() -> returns an iterable of all current existing values

    >unpack() -> returns the address as a string
    
    """
    def __init__(self, parsed_address):

        self.address = AddressContainer(
            Component(component_name='AddressNumber', component_value=''),
            Component(component_name='AdditionalAddressNumber', component_value=''),
            Component(component_name='StreetNamePreDirectional', component_value=''),
            Component(component_name='StreetNamePreType', component_value=''),
            Component(component_name='StreetName', component_value=''),
            Component(component_name='StreetNamePostType', component_value=''),
            Component(component_name='StreetNamePostDirectional', component_value=''),
            Component(component_name='PlaceName', component_value=''),
            Component(component_name='StateName', component_value=''),
            Component(component_name='ZipCode', component_value=''),
            Component(component_name='ZipCodeExtension', component_value='')
        )
        
        self.keys = tuple(self.address.keys())

        #Set values equal to given values from parameter
        self.initialize_address_components(parsed_address)
        #self.initialize_address(components)
    
    ##### NEW METHODS
    def __eq__(self, other):
        #TODO write better function
        return tuple(self.get_existing_values()) == tuple(other.get_existing_values())
    
    def __repr__(self):
        returnstring = ''
        for index, _ in enumerate(self.keys):
            if self.address[self.keys[index]]:
                if self.keys[index] != 'AdditionalAddressNumber':
                    returnstring += self.address[self.keys[index]]
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
        for component_index in range(index + 1, len(self.address)):
            if self.address[self.keys[component_index]]:
                return self.keys[component_index]
        return None

    def get_address(self): ##DONE
        """Returns the main storage variable."""
        return self.address

    def __getitem__(self, component_name): ##DONE
        return self.address[component_name]
    
    def get_existing_values(self): #DONE
        """Returns an iterable of all existing values."""
        return (value for value in self.address.values() if value)

    def set_address_component_v2(self, component): #DONE
        if component in self.address:
            self.address[component.name] = component.value if component.value else ''
    
    def __setitem__(self, component_name, component_value): #DONE
        if component_name in self.keys:
            self.address[component_name] = component_value if component_value else '' 
    
    def clear_address_component_v2(self, component):
        if component in self.address:
            self.address[component.name] = ''
   
    def switch_components_v2(self, first_component, second_component):
        self.address[first_component.name], self.address[second_component.name] = self.address[second_component.value], self.address[first_component.value]
    
    def clear_address(self): #DONE
        """Removes all values for all components."""
        for component_name in self.keys:
            self.address[component_name] = ''
    
    def unpack(self):
        """Returns the address as a string."""
        return self.__repr__()
    
    def initialize_address(self, *components):
        for component in components:
            if component in self.address:
                self.address[component.name] = component.value if component.value else ''
    ##### NEW METHODS


    def initialize_address_components(self, parsed_address): #TO BE REMOVED
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
            if component in self.keys:
                if value:
                    self.address[component] = value

    def clear_address_component(self, component):
        """Removes the value for a given component."""
        if component in self.keys:
            self.address[component] = ''
             
    def switch_components(self, first_component, second_component):
        """Switches the values of two given components."""
        self.address[first_component], self.address[second_component] = self.address[second_component], self.address[first_component]
