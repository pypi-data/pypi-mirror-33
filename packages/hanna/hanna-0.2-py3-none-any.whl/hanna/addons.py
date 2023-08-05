import copy

import hanna
from . import configuration
from .parameters import Parameter, Wrapper


class AddOn:
    @classmethod
    def install(cls):
        pass

    @classmethod
    def uninstall(cls):
        pass


class AutocompleteParameterNames(AddOn):
    """
    This add-on enables autocomplete of parameter names when being set on a `Configurable` subclass
    outside of a class definition.
    
    .. warning::
       As a consequence of installing this add-on the `Configurable` class will receive a specific
       metaclass which handles the autocomplete. In case you use custom metaclass as well this
       might lead to conflicts.
       
    .. note::
       As a consequence of installing this add-on each subclass of `Configurable` which specifies
       a `path` during class definition will receive an additional class attribute `_config_path`
       which holds the value of the specified path.
    """

    Configurable = configuration.Configurable

    class AutoCompleter(type):
        @classmethod
        def __prepare__(mcs, name, bases, **kwargs):
            namespace = super().__prepare__(name, bases)
            if 'path' in kwargs:
                namespace['_config_path'] = kwargs.get('path')
            return namespace

        def __setattr__(self, key, value):
            if isinstance(value, (Parameter, Wrapper)):
                value = copy.deepcopy(value)
                value.__set_name__(self, key)
                config_path = getattr(self, '_config_path', '')
                if config_path:
                    value.name = f'{config_path}.{value.name}'
            super().__setattr__(key, value)

    @classmethod
    def install(cls):
        super().install()
        configuration.Configurable = cls.AutoCompleter(
            configuration.Configurable.__name__,
            configuration.Configurable.__bases__,
            dict(**configuration.Configurable.__dict__)
        )
        hanna.Configurable = configuration.Configurable

    @classmethod
    def uninstall(cls):
        super().uninstall()
        configuration.Configurable = cls.Configurable
        hanna.Configurable = cls.Configurable
