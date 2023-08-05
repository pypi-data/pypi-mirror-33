# Set a backend for physical units, e.g.:
#    * numericalunits (https://pypi.org/project/numericalunits/)
#    * pint (https://pint.readthedocs.io/en/latest/)
#    * units (https://pypi.org/project/units/)

try:
    import pint
except ImportError:
    pint = None

try:
    import numericalunits
except ImportError:
    numericalunits = None

try:
    import units
except ImportError:
    units = None


class Engine:
    backend = None
    backend_url = None

    def __init__(self):
        if self.backend is None:
            raise NotImplementedError(f'{self.__class__.__name__} engine is not available. '
                                      f'Please install the {self.backend_url} package first.')

    def __getitem__(self, item):
        raise NotImplementedError

    def convert(self, quantity, to_unit):
        raise NotImplementedError


class NumericalUnits(Engine):
    backend = numericalunits
    backend_url = 'https://pypi.org/project/numericalunits/'

    def __init__(self):
        super().__init__()

    def __getitem__(self, item):
        return getattr(self.backend, item)

    def convert(self, quantity, to_unit):
        return quantity[0] * (quantity[1] / to_unit)


class Pint(Engine):
    backend = pint
    backend_url = 'https://pypi.org/project/Pint/'

    def __init__(self):
        super().__init__()
        self._ur = self.backend.UnitRegistry()

    def __getitem__(self, item):
        return getattr(self._ur, item)

    def convert(self, quantity, to_unit):
        return (quantity[0] * quantity[1]).to(to_unit).magnitude


class Units(Engine):
    backend = units
    backend_url = 'https://pypi.org/project/units/'

    def __init__(self):
        super().__init__()
        from units.predefined import define_units
        define_units()

    def __getitem__(self, item):
        return units.unit(item)

    def convert(self, quantity, to_unit):
        return to_unit(quantity[1](quantity[0])).num


class UnitsProxy:
    def __init__(self):
        self._engine = None

    def __getattr__(self, item):
        if isinstance(item, str):
            return self._engine[item]
        return item

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._engine[item]
        return item

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, cls):
        if not issubclass(cls, Engine):
            raise TypeError(f'Units engine must be a subclass of {Engine.__name__}')
        self._engine = cls()

    def convert(self, quantity, to_unit):
        """
        Convert the given quantity to different units.
        
        quantity : tuple, length 2
            First entry is the magnitude, second entry is the unit.
        to_unit : unit
            The unit to which the quantity is converted.
            
        Returns
        -------
        converted : float
            The magnitude of the converted quantity.
        """
        return self.engine.convert(quantity, to_unit)
