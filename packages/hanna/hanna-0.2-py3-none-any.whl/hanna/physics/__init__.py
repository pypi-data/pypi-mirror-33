import warnings
from .units import UnitsProxy, Pint

units = UnitsProxy()
try:
    units.engine = Pint
except NotImplementedError:
    warnings.warn('The default units engine is not available. You need to set the engine manually '
                  'via `from hanna.physics import units; units.engine = ...`.')
del UnitsProxy
