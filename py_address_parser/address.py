from .address_components import address_components
from .componentcontainer import ComponentContainer
from .component import AddressComponent


class Address(object):
    """
    Description
    -----------
    >A Class used to represent an address. Contains multiple components.

    Paramaters
    ----------
    >

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
    >

    """

    def __init__(self, *components):

        self.__address = ComponentContainer(
            *[AddressComponent(component_name=component) for component in address_components]
        )

        self.__keys = tuple(self.__address.keys())

        # Set values equal to given values from parameter
        if components:
            self.initialize_address(components)

    # NEW METHODS
    def __eq__(self, other):
        # TODO write better function
        return tuple(self.get_existing_values()) == tuple(other.get_existing_values())

    def __str_repr__(self):
        returnstring = ''
        for index, _ in enumerate(self.__keys):
            if self.__address[self.__keys[index]].exists():
                if self.__keys[index] != 'AdditionalAddressNumber':
                    returnstring += self.__address[self.__keys[index]].value
                    if self.next_component(index) in ['PlaceName', 'StateName']:
                        returnstring += ', '
                    elif self.next_component(index) == 'ZipCodeExtension' \
                            and self.__address['ZipCodeExtension'].exists():
                        returnstring += '-'
                    else:
                        returnstring += ' '
        return returnstring

    def __repr__(self):
        return f'<Address object \'{self.__str_repr__()}\'>'

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
            if self.__address[self.__keys[component_index]].value:
                return self.__keys[component_index]
        return None

    def __contains__(self, component_name):
        return component_name in self.__address

    def has_component(self, component):
        return component.name in self.__address

    def __getitem__(self, component_name):  # DONE
        return self.__address[component_name]

    def get_full_zipcode(self):
        zipcode = self.__address['ZipCode']['value']
        zipcode = '{zipcode}{extension}'.format(
            zipcode=zipcode if zipcode else '',
            extension=self.__address['ZipCodeExtension']['value'] if zipcode and self.__address['ZipCodeExtension']['value'] else ''
        )
        return zipcode if zipcode else None

    def get_existing_values(self):  # DONE
        """Returns an iterable of all existing values."""
        return (value.value for value in self.__address.values() if value.value)

    def get_existing_keys(self):
        return (key for key in self.__address.keys() if self.__address[key].value)

    def set_address_component(self, component):  # DONE
        if component in self.__address:
            self.__address[component.name] = component if component.value else AddressComponent(
                component.name, '')

    def __setitem__(self, component_name, component_value):  # DONE
        if component_name in self.__keys:
            self.__address[component_name] = AddressComponent(
                component_name, component_value) if component_value else AddressComponent(component_name, '')

    def clear_address_component_v2(self, component):
        if component in self.__address:
            self.__address[component.name] = AddressComponent(component.name, '')

    def switch_components_v2(self, first_component, second_component):
        self.__address[first_component.name], self.__address[second_component.name] = self.__address[
            second_component.value], self.__address[first_component.value]

    def clear_address(self):  # DONE
        """Removes all values for all components."""
        for component_name in self.__keys:
            self.__address[component_name] = AddressComponent(component_name, '')

    def as_string(self):
        """Returns the address as a string."""
        return self.__str_repr__()

    def as_dict(self):
        """Returns the address ad a python dictionary"""
        return {key: value for key, value in self.__address.items()}

    def initialize_address(self, *components):
        for component_container in components:
            for component in component_container.values():
                if self.__address.has_component(component):
                    self.__address[component.name] = component if component.value else AddressComponent(
                        component.name, '')

    def get_all_components(self):
        return (component for component in self.__address.values())

    # OLD METHODS
    def clear_address_component(self, component_name):
        """Removes the value for a given component."""
        if component_name in self.__keys:
            self.__address[component_name] = AddressComponent(component_name, '')

    def switch_components(self, first_component, second_component):
        """Switches the values of two given components."""
        self.__address[first_component], self.__address[second_component] = self.__address[second_component], self.__address[first_component]

    def keys(self):
        return tuple(self.get_existing_keys())

    def values(self):
        return tuple(self.get_existing_values())

    def items(self):
        return ((key, self.__address[key].value) for key in self.__keys if self.__address[key].value)

    def components(self):
        return tuple(component for component in self.__address.values() if component.value)
