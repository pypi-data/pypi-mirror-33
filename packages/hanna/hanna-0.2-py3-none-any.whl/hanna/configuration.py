from pyhocon import ConfigTree
from pyhocon.exceptions import ConfigMissingException

from .parameters import Parameter, Wrapper


class Configurable:
    @classmethod
    def __init_subclass__(cls, path='', adopt=True):
        if path:
            for par in cls.get_parameters():
                par.name = '{}.{}'.format(path, par.name)
        if adopt:
            adopted = []
            for base in filter(lambda x: issubclass(x, Configurable), cls.__bases__):
                adopted.extend(base.get_parameters())
            for par in filter(lambda x: not hasattr(cls, x.field_name), adopted):
                setattr(cls, par.field_name, par)

    def __init__(self, configuration=None):
        def load_parameter(par):
            if par.name in ('', '.'):
                return par.load(configuration)
            try:
                specification = configuration[par.name]
            except ConfigMissingException as err:
                if par.optional:
                    return par.default
                else:
                    raise err
            else:
                return par.load(specification)

        if configuration is None:
            configuration = ConfigTree()  # To prevent TypeError later on, when subscripting.

        for parameter in self.get_parameters():
            setattr(self, parameter.field_name, load_parameter(parameter))

    @classmethod
    def get_parameters(cls):
        return filter(
            lambda y: isinstance(y, (Parameter, Wrapper)),
            map(
                lambda x: getattr(cls, x),
                dir(cls)
            )
        )
