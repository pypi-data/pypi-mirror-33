from .configuration import Configurable
from .parameters import Bool, Integer, Number, String, PhysicalQuantity, \
    ComplementaryGroup, Group, Vector, VectorFactory

Vectors = VectorFactory()
del VectorFactory
