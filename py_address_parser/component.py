from .address_components import address_components


class AddressComponent(object):

    def __init__(self, component_name, component_value=None):
        if self.validate_name(component_name):
            self.name = component_name
            self.value = component_value
        else:
            self.return_invalid()

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __repr__(self):
        return f'{self.name}: {str(self.value)}'

    def get_component(self):
        return (self.name, self.value)

    def set_name(self, component_name):
        self.name = component_name if self.validate_name(
            component_name) else None

    def __getitem__(self, item_name):
        if item_name == 'name':
            return self.name if self.name else None
        elif item_name == 'value':
            return self.value if self.value else None
        return None

    def set_value(self, component_value):
        self.value = component_value

    def validate_name(self, component_name):
        if isinstance(component_name, str) and component_name in address_components:
            return True
        raise TypeError('Component name should be a string')

    def __value__(self):
        return self.value if self.value else None

    def exists(self):
        if self.value:
            return True
        return False
