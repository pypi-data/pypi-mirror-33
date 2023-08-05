from collections import OrderedDict
import copy
from functools import partial, reduce
import re
from typing import Any, Union

from pyhocon import ConfigTree
from pyhocon.exceptions import ConfigMissingException
try:
    import numpy as np
except ImportError:
    np = None
try:
    from scipy.constants import physical_constants
except ImportError:
    physical_constants = None

from hanna.physics import units
from hanna.utils import safe_math_eval


class Parameter:
    def __or__(self, parameter):
        return self.fallback(parameter)

    def __rmul__(self, times):
        vector = Vector(type(self), n=times, as_=tuple)
        vector.template = self
        return vector

    def __init__(self, name=None, default=None, optional=False, info=None, choices=None):
        self.name = name
        self._default = default
        self.optional = default is not None or optional
        self.info = info
        self.choices = choices or []
        self._field_name = None
        self.constraints = [Constraint(lambda x: not self.choices or x in self.choices,
                                       lambda x: f'Illegal choice ({x} not in {self.choices})')]
        self.transformations = []

    def __set_name__(self, owner, name):
        self._field_name = name
        name = name.lstrip('_')
        if self.name is None:
            self.name = name
        elif self.name.endswith('.'):
            self.name += name

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(name={repr(self.name)}, default={repr(self._default)}, '
            f'optional={repr(self.optional)}, info={repr(self.info)}, choices={self.choices or None})'
        )

    def __eq__(self, val):
        self.constraints.append(Constraint(lambda x: x == val, f'Not equal ({{value}} ≠ {val})'))
        return self

    def __ge__(self, lim):
        self.constraints.append(Constraint(lambda x: x >= lim, f'Too small ({{value}} < {lim})'))
        return self

    def __gt__(self, lim):
        self.constraints.append(Constraint(lambda x: x > lim, f'Too small ({{value}} ≤ {lim})'))
        return self

    def __le__(self, lim):
        self.constraints.append(Constraint(lambda x: x <= lim, f'Too large ({{value}} > {lim})'))
        return self

    def __lt__(self, lim):
        self.constraints.append(Constraint(lambda x: x < lim, f'Too large ({{value}} ≥ {lim})'))
        return self

    def __ne__(self, val):
        self.constraints.append(Constraint(lambda x: x != val, f'Must not be equal ({{value}} = {val})'))
        return self

    def __rshift__(self, transformation):
        try:
            return self.transform(*transformation)
        except TypeError:
            return self.transform(transformation)

    @property
    def abs(self):
        return Characteristic(self, abs)

    @property
    def len(self):
        return Characteristic(self, len)

    @property
    def field_name(self):
        return self._field_name or self.name.rsplit('.', 1)[-1].lower()

    @property
    def default(self):
        if self._default is None and not self.optional:
            raise AttributeError
        return self._default

    @default.setter
    def default(self, value):
        self._default = value
        self.optional = True

    def constrain(self, constraint, error_msg=''):
        self.constraints.append(Constraint(constraint, error_msg))
        return self

    def fallback(self, parameter):
        return FallbackGroup(self, [parameter])

    def load(self, value: Union[str, list, dict, ConfigTree]) -> Any:
        result = reduce(lambda x, t: t(x), self.transformations, value)
        for constraint in self.constraints:
            try:
                constraint(result)
            except ValueError as err:
                raise ValueError(f'"{self.name}" {str(err)}')
        return result

    def transform(self, *transformations):
        self.transformations.extend(transformations)
        return self

    def valid(self, result: Any) -> bool:
        return all(c(result) for c in self.constraints)


class FormulaParameter(Parameter):
    formulas = True
    pattern = '^.*$'
    illegal_patterns = tuple()
    type_ = str

    def __init__(self, name=None, default=None, optional=False, info=None, choices=None,
                 pattern=None, formulas=None):
        super().__init__(name, default, optional, info, choices)
        if pattern is not None:
            self.pattern = pattern
        if formulas is not None:
            self.formulas = formulas

    def load(self, specification):
        if self.pattern:
            specification = str(specification)
            match = re.match(self.pattern, specification)
            if match is None:
                raise ValueError(f'"{self.name}" Does not match pattern \'{self.pattern}\' '
                                 f'(\'{specification}\')')
            illegal = list(filter(
                lambda pattern: re.search(pattern, specification) is not None,
                self.illegal_patterns
            ))
            if illegal:
                match = re.search(illegal[0], specification)
                raise ValueError(f'"{self.name}" Contains illegal patterns '
                                 f'({repr(match.group())} forbidden by {repr(illegal[0])})')
        if self.formulas and isinstance(specification, str):
            specification = self.evaluate_formula(specification)
        return super().load(self.type_(specification))

    def evaluate_formula(self, formula):
        raise NotImplementedError


class Bool(FormulaParameter):
    pattern = '^[Tt]rue|[Ff]alse$'
    type_ = bool

    def evaluate_formula(self, formula):
        return formula.lower() == 'true'


class Integer(FormulaParameter):
    pattern = r'[()*+-/\s\d]+'
    illegal_patterns = ('[^/]/[^/]', '[a-zA-Z]', '{.*}', '\[.*\]')
    type_ = int

    def evaluate_formula(self, formula):
        return safe_math_eval(formula)


class Number(FormulaParameter):
    pattern = r'[()*+-/\s\da-zE.]+'
    illegal_patterns = Integer.illegal_patterns[2:]
    type_ = float
    np_members = ['sin', 'cos', 'tan', 'arcsin', 'arccos', 'arctan', 'hypot', 'arctan2',
                  'degrees', 'radians', 'unwrap', 'deg2rad', 'rad2deg', 'sinh', 'cosh', 'tanh',
                  'arcsinh', 'arccosh', 'arctanh', 'around', 'round_', 'rint', 'fix', 'floor',
                  'ceil', 'trunc', 'exp', 'expm1', 'exp2', 'log', 'log10', 'log2', 'log1p',
                  'logaddexp', 'logaddexp2', 'i0', 'sinc', 'sqrt', 'cbrt', 'square', 'absolute',
                  'fabs', 'sign', 'pi']

    def evaluate_formula(self, formula):
        scope = {m: getattr(np, m) for m in self.np_members} if np is not None else None
        return safe_math_eval(formula, locals_dict=scope)


class String(FormulaParameter):
    def evaluate_formula(self, formula):
        return formula


class PhysicalQuantity(FormulaParameter):
    pattern = r'[{}()*+-/\s\da-zA-Z.^]+\s?\[.+\]'
    type_ = float

    def __init__(self, name=None, default=None, optional=False, info=None, choices=None,
                 pattern=None, formulas=None, *, unit):
        super().__init__(name, default, optional, info, choices, pattern, formulas)
        self.unit = unit

    def evaluate_formula(self, formula):
        scope = {}
        if np is not None:
            scope = {m: getattr(np, m) for m in Number.np_members}
        if physical_constants is not None:
            scope.update({self.convert_constant_name(k): v[0] for k, v in physical_constants.items()})
            for key in physical_constants.keys():
                key_id = '{' + key + '}'
                if key_id in formula:
                    formula = formula.replace(key_id, self.convert_constant_name(key))
        m_units = re.search('\s*\[(.+)\]$', formula)
        unit = self.derive_unit(m_units.groups()[0])
        magnitude = safe_math_eval(formula.replace(m_units.group(), ''), locals_dict=scope)
        declared_unit = self.derive_unit(self.unit)
        return units.convert((magnitude, unit), declared_unit)

    @staticmethod
    def derive_unit(unit):
        if isinstance(unit, str):
            d_units = {u_id: units[u_id]
                       for u_id in re.findall(r'[a-zA-Z][a-zA-Z_0-9]*', unit)}
            return eval(unit.replace('^', '**'), {'__builtins__': None}, d_units)
        return unit

    @staticmethod
    def convert_constant_name(name):
        replacements = [('/', '_over_'), ('-', '_'), ('.', ''), ('(', '_'), (')', '_'), (',', ''),
                        ('{', ''), ('}', ''), (' ', '_')]
        return re.sub('__+', '_', reduce(lambda n, r: n.replace(*r), replacements, name))


class Characteristic:
    def __init__(self, parameter, func):
        self.parameter = parameter
        self.func = func

    def __eq__(self, val):
        self.parameter.constraints.append(Constraint(
            lambda x: self.func(x) == val,
            f'Not equal ({self.func.__name__}({{value}}) ≠ {val})'
        ))
        return self.parameter

    def __ge__(self, lim):
        self.parameter.constraints.append(Constraint(
            lambda x: self.func(x) >= lim,
            f'Too small ({self.func.__name__}({{value}}) < {lim})'
        ))
        return self.parameter

    def __gt__(self, lim):
        self.parameter.constraints.append(Constraint(
            lambda x: self.func(x) > lim,
            f'Too small ({self.func.__name__}({{value}}) ≤ {lim})'
        ))
        return self.parameter

    def __le__(self, lim):
        self.parameter.constraints.append(Constraint(
            lambda x: self.func(x) <= lim,
            f'Too large ({self.func.__name__}({{value}}) > {lim})'
        ))
        return self.parameter

    def __lt__(self, lim):
        self.parameter.constraints.append(Constraint(
            lambda x: self.func(x) < lim,
            f'Too large ({self.func.__name__}({{value}}) ≥ {lim})'
        ))
        return self.parameter

    def __ne__(self, val):
        self.parameter.constraints.append(Constraint(
            lambda x: self.func(x) != val,
            f'Must not be equal ({self.func.__name__}({{value}}) = {val})'
        ))
        return self.parameter


class Constraint:
    def __init__(self, func, error_msg):
        self.func = func
        self.error_msg = error_msg

    def __call__(self, val):
        if not self.func(val):
            if callable(self.error_msg):
                raise ValueError(self.error_msg(val))
            try:
                error_msg = self.error_msg.format(value=repr(val))
            except KeyError:
                error_msg = self.error_msg
            raise ValueError(error_msg)
        return True


class VectorFactory:
    def __getitem__(self, kind):
        return partial(Vector, kind=kind)

    @property
    def container(self):
        return Vector.container

    @container.setter
    def container(self, container):
        Vector.container = container


class Vector(Parameter):
    container = list

    def __init__(self, kind, name=None, default=None, optional=False, info=None, choices=None,
                 n=None, as_=None, **kwargs):
        super().__init__(name, default, optional, info, choices)
        self.template = kind(name=name, **kwargs)
        if isinstance(n, int):
            if n <= 0:
                raise ValueError('Number of elements must be greater than zero')
            _ = self.len == n
        if as_ is not None:
            self.container = as_

    def __abs__(self):
        raise NotImplementedError

    def __eq__(self, val):
        self.template.__eq__(val)
        return self

    def __ge__(self, lim):
        self.template.__ge__(lim)
        return self

    def __gt__(self, lim):
        self.template.__gt__(lim)
        return self

    def __le__(self, lim):
        self.template.__le__(lim)
        return self

    def __lt__(self, lim):
        self.template.__lt__(lim)
        return self

    def __ne__(self, val):
        self.template.__ne__(val)
        return self

    def load(self, value: list):
        result = []
        for i, x in enumerate(value):
            # Set name in order to have error messages displayed correctly.
            self.template.name = f'{self.name}[{i}]'
            result.append(self.template.load(x))
        self.template.name = None
        return super().load(self.container(result))

    def as_(self, container):
        self.container = container
        return self


class Wrapper:
    def __init__(self, name=None, info=None):
        self.info = info
        self.transformations = []
        self.name = name or '.'
        self.field_name = None

    def __set_name__(self, owner, name):
        self.field_name = name

    def __repr__(self):
        return f'{self.__class__.__name__}(name={repr(self.name)}, info={repr(self.info)})'

    def __rshift__(self, transformation):
        try:
            return self.transform(*transformation)
        except TypeError:
            return self.transform(transformation)

    def load(self, value):
        return reduce(lambda x, t: t(x), self.transformations, value)

    def transform(self, *transformations):
        self.transformations.extend(transformations)
        return self


class Group(Wrapper):
    container = dict

    def __init__(self, *members, name=None, info=None, as_=None):
        super().__init__(name, info)
        self.members = list(members)
        if as_ is not None:
            self.container = as_

    def __iadd__(self, parameter):
        self.add(parameter)
        return self

    def add(self, parameter):
        self.members.append(parameter)

    def as_(self, container):
        self.container = container
        return self

    def extend(self, other):
        new_members = [copy.copy(m) for m in other.members]
        for member in new_members:
            if other.name:
                member.name = f'{other.name}.{member.name}'
        self.members.extend(new_members)

    def load(self, value: ConfigTree):
        result = OrderedDict()
        for member in self.members:
            result[member.name] = member.load(value[member.name])
        if self.container in (list, tuple):
            result = self.container(result.values())
        else:
            result = self.container(**result)
        return super().load(result)


class FallbackGroup(Wrapper):
    def __init__(self, primary, proxies, name=None, info=None):
        super().__init__(name, info)
        self.primary = primary
        self.proxies = proxies

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        self.primary.__set_name__(owner, name)

    def __or__(self, parameter):
        return self.fallback(parameter)

    @property
    def optional(self):
        return self.primary.optional or any(map(lambda p: p.optional, self.proxies))

    @optional.setter
    def optional(self, x):
        pass

    def load(self, config):
        for parameter in [self.primary] + self.proxies:
            try:
                return parameter.load(config[parameter.name])
            except ConfigMissingException:
                continue
        for parameter in [self.primary] + self.proxies:
            if parameter.optional:
                return parameter.default
        raise ConfigMissingException(
            f'"{self.primary.name}" No fallback found '
            f'(checked the following parameters: {", ".join(map(lambda p: p.name, self.proxies))})'
        )

    def fallback(self, parameter):
        self.proxies.append(parameter)
        return self


class ComplementaryGroup(Wrapper):
    container = dict

    def __init__(self, *members, name=None, info=None, as_=None):
        super().__init__(name, info)
        members, rules = zip(*members)
        self.members = members
        self.rules = rules
        if as_ is not None:
            self.container = as_

    def __iadd__(self, parameter_and_rule):
        self.add(*parameter_and_rule)
        return self

    def add(self, parameter, rule):
        self.members.append(parameter)
        self.rules.append(rule)

    def as_(self, container):
        self.container = container
        return self

    def load(self, config):
        missing = list(filter(lambda p: p[1].name not in config, enumerate(self.members)))
        if len(missing) != 1:
            raise ValueError(f'"{self.name}" Too {"many" if not missing else "few"} '
                             f'parameters were specified ({abs(len(missing) - 1)})')

        members = [x for x in self.members]
        rules = [x for x in self.rules]
        complement = members.pop(missing[0][0])
        completion_rule = rules.pop(missing[0][0])

        result = OrderedDict()
        for member in members:
            result[member.name] = member.load(config[member.name])
        result[complement.name] = completion_rule(**result)

        if self.container in (list, tuple):
            result = self.container(result.values())
        else:
            result = self.container(**result)

        return super().load(result)
