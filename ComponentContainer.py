from Component import Component

class ComponentContainer(dict): #TODO make set instead of dict
    def __init__(self, *components):
        for component in components:
            self.__dict__[component.name] = component

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, component):
        del self.__dict__[component.name]

    def clear(self):
        return self.__dict__.clear()

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()
    
    def has_component(self, component):
        return component.name in self.__dict__

    def __contains__(self, component_name):
        return component_name in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)
