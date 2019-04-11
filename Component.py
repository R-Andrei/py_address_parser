

class Component(object):
    def __init__(self, component_name, component_value):
        if self.validate_name(component_name):
            self.name = component_name
            self.value = component_value
        else:
            raise TypeError('Component name should be a string.')

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value
    
    def __repr__(self):
        return self.name + ': ' + str(self.value) if self.value else self.name + ': ' + str(None)

    def get_component(self):
        return (self.name, self.value)

    def set_name(self, component_name):
        if self.validate_name(component_name):
            self.name = component_name
        else:
            raise TypeError('Component name should be a string.')

    def set_value(self, component_value):
        self.value = component_value
    
    def validate_name(self, component_name):
        return True if isinstance(component_name, str) else False

