from collections import namedtuple
from unittest import TestCase
import unittest

import numpy as np
from pyhocon import ConfigFactory
from pyhocon.exceptions import ConfigMissingException
from scipy.constants import physical_constants

from hanna import Integer, Number, PhysicalQuantity, String
from hanna import ComplementaryGroup, Group, Vector, Vectors
from hanna.configuration import Configurable
from hanna.parameters import FallbackGroup
from hanna.physics import units
from hanna.physics.units import NumericalUnits, Pint, Units


class TestGeneral(TestCase):
    def test_underscores(self):
        class Test(Configurable):
            _foo = String()
            _bar = Integer()

        self.assertEqual(Test._foo.name, 'foo')
        self.assertEqual(Test._bar.name, 'bar')


class TestSections(TestCase):
    def test_general(self):
        class Book(Configurable):
            title = String()
            year = Integer()

        self.assertEqual(Book.title.name, 'title')
        self.assertEqual(Book.year.name, 'year')

        title, year = 'some title', 2018
        book = Book(ConfigFactory.from_dict(dict(title=title, year=year)))
        self.assertEqual(book.title, title)
        self.assertEqual(book.year, year)

    def test_at_class_creation(self):
        class Book(Configurable, path='book'):
            title = String()
            year = Integer()

        self.assertEqual(Book.title.name, 'book.title')
        self.assertEqual(Book.year.name, 'book.year')

        title, year = 'some title', 2018
        book = Book(ConfigFactory.from_dict({
            'book': {
                'title': title,
                'year': year,
            }
        }))
        self.assertEqual(book.title, title)
        self.assertEqual(book.year, year)

        class Book(Configurable, path='library.book'):
            title = String()
            year = Integer()

        self.assertEqual(Book.title.name, 'library.book.title')
        self.assertEqual(Book.year.name, 'library.book.year')

        title, year = 'some title', 2018
        book = Book(ConfigFactory.from_dict({
            'library': {
                'book': {
                    'title': title,
                    'year': year,
                }
            }
        }))
        self.assertEqual(book.title, title)
        self.assertEqual(book.year, year)

    def test_as_part_of_the_name(self):
        class Book(Configurable):
            title = String('library.book.title')
            year = Integer('library.book.year')

        self.assertEqual(Book.title.name, 'library.book.title')
        self.assertEqual(Book.year.name, 'library.book.year')

        title, year = 'some title', 2018
        book = Book(ConfigFactory.from_dict({
            'library': {
                'book': {
                    'title': title,
                    'year': year,
                }
            }
        }))
        self.assertEqual(book.title, title)
        self.assertEqual(book.year, year)

    def test_in_place_of_the_name(self):
        class Book(Configurable):
            title = String('library.book.')
            year = Integer('library.book.')

        self.assertEqual(Book.title.name, 'library.book.title')
        self.assertEqual(Book.year.name, 'library.book.year')

        title, year = 'some title', 2018
        book = Book(ConfigFactory.from_dict({
            'library': {
                'book': {
                    'title': title,
                    'year': year,
                }
            }
        }))
        self.assertEqual(book.title, title)
        self.assertEqual(book.year, year)

        title_par = String('library.book.')
        self.assertEqual(title_par.name, 'library.book.')

        class Book(Configurable):
            title = title_par

        self.assertEqual(Book.title.name, 'library.book.title')

    def test_combinations(self):
        class Book(Configurable, path='library'):
            title = String('book.')
            year = Integer('book.year')

        self.assertEqual(Book.title.name, 'library.book.title')
        self.assertEqual(Book.year.name, 'library.book.year')

        title, year = 'some title', 2018
        book = Book(ConfigFactory.from_dict({
            'library': {
                'book': {
                    'title': title,
                    'year': year,
                }
            }
        }))
        self.assertEqual(book.title, title)
        self.assertEqual(book.year, year)


class TestTransformations(TestCase):
    def test_1(self):
        class Book(Configurable):
            n_words_1 = String('title').transform(str.split, len)
            n_words_2 = String('title').transform(lambda x: len(x.split()))
            century = Integer('year').transform(lambda x: x // 1000 + 1)

        self.assertEqual(len(Book.n_words_1.transformations), 2)
        self.assertEqual(len(Book.n_words_2.transformations), 1)
        self.assertEqual(len(Book.century.transformations), 1)

        book = Book(ConfigFactory.from_dict(dict(title='This is the title', year=2018)))
        self.assertEqual(book.n_words_1, 4)
        self.assertEqual(book.n_words_2, 4)
        self.assertEqual(book.century, 3)

        import math

        class Test(Configurable):
            p1 = Number('number').transform(int)
            p2 = Number('number').transform(math.floor)
            p3 = Number('number').transform(math.ceil)
            p4 = Integer().transform(lambda x: x ** 2)
            p5 = Integer().transform(lambda x: 'a' * x)

        test = Test(ConfigFactory.from_dict(dict(number=3.14, p4=5, p5=3)))
        self.assertEqual(test.p1, 3)
        self.assertEqual(test.p2, 3)
        self.assertEqual(test.p3, 4)
        self.assertEqual(test.p4, 25)
        self.assertEqual(test.p5, 'aaa')

    def test_2(self):
        class Test(Configurable):
            p1 = Integer('p').transform(lambda x: x**2, lambda x: x**3, lambda x: x**4)
            p2 = Integer('p').transform(lambda x: x**2).transform(lambda x: x**3).transform(lambda x: x**4)

        self.assertEqual(len(Test.p1.transformations), 3)
        self.assertEqual(len(Test.p2.transformations), 3)

        test = Test(ConfigFactory.from_dict(dict(p=2)))
        self.assertEqual(test.p1, 16777216)
        self.assertEqual(test.p2, 16777216)

    def test_syntactic_sugar(self):
        class Test(Configurable):
            p1 = Integer('p') >> (lambda x: x**2, lambda x: x**3, lambda x: x**4)
            p2 = Integer('p') >> (lambda x: x**2) >> (lambda x: x**3) >> (lambda x: x**4)

        self.assertEqual(len(Test.p1.transformations), 3)
        self.assertEqual(len(Test.p2.transformations), 3)

        test = Test(ConfigFactory.from_dict(dict(p=2)))
        self.assertEqual(test.p1, 16777216)
        self.assertEqual(test.p2, 16777216)


class TestConstraints(TestCase):
    def test_integer(self):
        class Test(Configurable):
            p1 = Integer() >= 1
            p2 = Integer() > 2
            p3 = Integer() <= 3
            p4 = Integer() < 4
            p5 = Integer() == 5  # Not really useful for built-in types but we'll test it anyway.
            p6 = Integer() != 6

        try:
            Test(ConfigFactory.from_dict(dict(p1=1, p2=3, p3=3, p4=3, p5=5, p6=5)))
        except ValueError:
            self.fail('Constraints not applied correctly')

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=0, p2=3, p3=3, p4=3, p5=5, p6=5)))
        self.assertEqual('"p1" Too small (0 < 1)', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=1, p2=2, p3=3, p4=3, p5=5, p6=5)))
        self.assertEqual('"p2" Too small (2 ≤ 2)', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=1, p2=3, p3=4, p4=3, p5=5, p6=5)))
        self.assertEqual('"p3" Too large (4 > 3)', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=1, p2=3, p3=3, p4=4, p5=5, p6=5)))
        self.assertEqual('"p4" Too large (4 ≥ 4)', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=1, p2=3, p3=3, p4=3, p5=6, p6=5)))
        self.assertEqual('"p5" Not equal (6 ≠ 5)', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=1, p2=3, p3=3, p4=3, p5=5, p6=6)))
        self.assertEqual('"p6" Must not be equal (6 = 6)', str(context.exception))

        class Test(Configurable):
            # noinspection PyTypeChecker
            p1 = 0 <= Integer() <= 2

        try:
            Test(ConfigFactory.from_dict(dict(p1=1)))
        except ValueError:
            self.fail('Constraints not applied correctly')

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=-1)))
        self.assertEqual('"p1" Too small (-1 < 0)', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=3)))
        self.assertEqual('"p1" Too large (3 > 2)', str(context.exception))

    def test_characteristics(self):
        class Test(Configurable):
            p1 = Integer().abs <= 5
            p2 = Integer().abs < 5
            p3 = Integer().abs >= 5
            p4 = Integer().abs > 5
            p5 = String().len <= 5
            p6 = String().len < 5
            p7 = String().len >= 5
            p8 = String().len > 5

        config = dict(
            p1=-5, p2=-4, p3=5, p4=6,
            p5='12345', p6='1234', p7='12345', p8='123456'
        )
        try:
            test = Test(ConfigFactory.from_dict(config))
        except ValueError:
            self.fail('Constraints not applied correctly')
        self.assertEqual(test.p1, config['p1'])
        self.assertEqual(test.p2, config['p2'])
        self.assertEqual(test.p3, config['p3'])
        self.assertEqual(test.p4, config['p4'])
        self.assertEqual(test.p5, config['p5'])
        self.assertEqual(test.p6, config['p6'])
        self.assertEqual(test.p7, config['p7'])
        self.assertEqual(test.p8, config['p8'])

    def test_custom_constraints(self):
        class Test(Configurable):
            p1 = Integer().constrain(lambda x: x <= 5, '')
            p2 = Integer().constrain(lambda x: x <= 5, 'Custom error message')
            p3 = Integer().constrain(lambda x: x <= 5, 'Wrong value: {value}')
            p4 = String().len > 5
            p5 = String().constrain(lambda x: len(x.split()) > 5, 'Not enough words: {value}')

        try:
            Test(ConfigFactory.from_dict(dict(p1=3, p2=3, p3=3, p4='123456', p5='1 2 3 4 5 6')))
        except ValueError:
            self.fail('Constraints not applied correctly')

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=8, p2=3, p3=3, p4='123456', p5='1 2 3 4 5 6')))
        self.assertEqual('"p1" ', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=3, p2=8, p3=3, p4='123456', p5='1 2 3 4 5 6')))
        self.assertEqual('"p2" Custom error message', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=3, p2=3, p3=8, p4='123456', p5='1 2 3 4 5 6')))
        self.assertEqual('"p3" Wrong value: 8', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=3, p2=3, p3=3, p4='12345', p5='1 2 3 4 5 6')))
        self.assertEqual('"p4" Too small (len(\'12345\') ≤ 5)', str(context.exception))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1=3, p2=3, p3=3, p4='123456', p5='1 2 3 4 5')))
        self.assertEqual('"p5" Not enough words: \'1 2 3 4 5\'', str(context.exception))


class TestVectors(TestCase):
    def test_general(self):
        class Test(Configurable):
            v = Vectors[Integer]()
        self.assertEqual(Test(ConfigFactory.from_dict(dict(v=[1, 2, 3]))).v, [1, 2, 3])
        Test.v = Vector(String, name='v')
        self.assertEqual(Test(ConfigFactory.from_dict(dict(v=['a', 'b', 'c']))).v, ['a', 'b', 'c'])

    def test_containers(self):
        class Test(Configurable):
            v1 = Vector(Integer, as_=tuple)
            v2 = Vector(Integer).as_(tuple)
            v3 = Vector(Integer, as_=set)
        test = Test(ConfigFactory.from_dict(dict(v1=[1, 2, 3], v2=[1, 2, 3], v3=[1, 1, 2, 2, 3])))
        self.assertEqual(test.v1, (1, 2, 3))
        self.assertEqual(test.v2, (1, 2, 3))
        self.assertEqual(test.v3, {1, 2, 3})

        Vector.container = tuple

        class Test(Configurable):
            v = Vector(Integer)
        self.assertEqual(Test(ConfigFactory.from_dict(dict(v=[1, 2, 3]))).v, (1, 2, 3))

        Vector.container = list

    def test_constraints(self):
        IntVector = Vectors[Integer]

        class Test(Configurable):
            v1 = IntVector() > 0

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(v1=[-1, 1])))
        self.assertEqual('"v1[0]" Too small (-1 ≤ 0)', str(context.exception))

        Test.v1 = Test.v1 <= 4
        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(v1=[1, 2, 3, 4, 5, 6, 7, 8])))
        self.assertEqual('"v1[4]" Too large (5 > 4)', str(context.exception))

        Test.v1 = IntVector(name='v1', n=3)
        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(v1=[1, 2])))
        self.assertEqual('"v1" Not equal (len([1, 2]) ≠ 3)', str(context.exception))

        Test.v1 = IntVector(name='v1').len > 2
        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(v1=[1, 2])))
        self.assertEqual('"v1" Too small (len([1, 2]) ≤ 2)', str(context.exception))

    def test_tuple_from_multiplication(self):
        class Test(Configurable):
            v = 3 * Integer()

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(v=[0, 1])))
        self.assertEqual('"v" Not equal (len((0, 1)) ≠ 3)', str(context.exception))
        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(v=[0, 1, 2, 3])))
        self.assertEqual('"v" Not equal (len((0, 1, 2, 3)) ≠ 3)', str(context.exception))

        self.assertEqual(Test(ConfigFactory.from_dict(dict(v=[0, 1, 2]))).v, (0, 1, 2))


class TestPatterns(TestCase):
    def test_strings(self):
        class Test(Configurable):
            p1 = String(pattern=r'Exactly \d+ times')

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1='Exactly two times')))
        self.assertEqual(
            '"p1" Does not match pattern \'Exactly \\d+ times\' (\'Exactly two times\')',
            str(context.exception)
        )

        self.assertEqual(
            Test(ConfigFactory.from_dict(dict(p1='Exactly 2 times'))).p1,
            'Exactly 2 times'
        )

    def test_integers(self):
        class Test(Configurable):
            p1 = Integer()
        self.assertEqual(Test(ConfigFactory.from_dict(dict(p1='-1'))).p1, -1)
        Test.p1 = Integer('p1', pattern=r'\d+')
        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.from_dict(dict(p1='-1')))
        self.assertEqual('"p1" Does not match pattern \'\\d+\' (\'-1\')', str(context.exception))
        self.assertEqual(Test(ConfigFactory.from_dict(dict(p1='123'))).p1, 123)
        self.assertEqual(Test(ConfigFactory.from_dict(dict(p1=123))).p1, 123)

    def test_deactivating_patterns(self):
        class Test(Configurable):
            p1 = Integer()
        with self.assertRaises(ValueError):
            Test(ConfigFactory.from_dict(dict(p1='1 / 2')))

        class Test(Configurable):
            p1 = Integer(pattern=False)
        self.assertEqual(Test(ConfigFactory.from_dict(dict(p1='1 / 2'))).p1, 0)


class TestGroups(TestCase):
    def test_general(self):
        class Test(Configurable):
            g = Group(String('first'), String('second'))
        self.assertEqual(Test.g.field_name, 'g')
        self.assertEqual(
            Test(ConfigFactory.parse_string('first = "1"\nsecond = "2"')).g,
            {'first': '1', 'second': '2'}
        )

    def test_containers(self):
        dim_type = namedtuple('dimensions', ['width', 'height'])

        class Test(Configurable):
            g1 = Group(Integer('width'), Integer('height'), as_=dim_type)
            g2 = Group(Integer('width'), Integer('height')).as_(dim_type)

        test = Test(ConfigFactory.parse_string('width = 1\nheight = 2'))
        self.assertEqual(type(test.g1), dim_type)
        self.assertEqual(repr(test.g1), 'dimensions(width=1, height=2)')
        self.assertEqual(type(test.g2), dim_type)
        self.assertEqual(repr(test.g2), 'dimensions(width=1, height=2)')

        class Test(Configurable):
            g1 = Group(Integer('a'), Integer('b'), Integer('c'), as_=tuple)
        test = Test(ConfigFactory.parse_string('a = 1\nb = 2\nc = 3'))
        self.assertEqual(test.g1, (1, 2, 3))

    def test_transformations(self):
        class Rectangle(Configurable):
            area = Group(Integer('width'), Integer('height')).transform(
                lambda x: x['width'] * x['height']
            )
        self.assertEqual(Rectangle(ConfigFactory.parse_string('width = 2\nheight = 3')).area, 6)

        class Rectangle(Configurable):
            area = Group(Integer('width'), Integer('height'), as_=tuple).transform(
                lambda x: x[0] * x[1]
            )
        self.assertEqual(Rectangle(ConfigFactory.parse_string('width = 2\nheight = 3')).area, 6)

        class Rectangle(Configurable):
            area = Group(Integer('width'), Integer('height'), as_=tuple) >> (lambda x: x[0] * x[1])
        self.assertEqual(Rectangle(ConfigFactory.parse_string('width = 2\nheight = 3')).area, 6)

    def test_sections(self):
        class Test(Configurable):
            g1 = Group(String('foo'), name='first.group')
            g2 = Group(String('bar'), name='second.group')

        test = Test(ConfigFactory.parse_string('first { group { foo = "foo-spec"}}\n'
                                               'second { group { bar = "bar-spec"}}'))
        self.assertEqual(test.g1, {'foo': 'foo-spec'})
        self.assertEqual(test.g2, {'bar': 'bar-spec'})

    def test_extensions(self):
        class Test(Configurable):
            g = Group(Integer('a'))
        Test.g.add(Integer('b'))
        Test.g += Integer('c')
        Test.g.extend(Group(Integer('d'), name='other'))

        test = Test(ConfigFactory.parse_string(
            'a = 1\n'
            'b = 2\n'
            'c = 3\n'
            'other {\n d = 4 }\n'
        ))
        self.assertEqual(test.g, {'a': 1, 'b': 2, 'c': 3, 'other.d': 4})


class TestChoices(TestCase):
    def test_general(self):
        class Test(Configurable):
            i = Integer(choices=(1, 2, 3))

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.parse_string('i = 0'))
        self.assertEqual('"i" Illegal choice (0 not in (1, 2, 3))', str(context.exception))
        self.assertEqual(Test(ConfigFactory.parse_string('i = 1')).i, 1)

    def test_extending(self):
        class Test(Configurable):
            i = Integer(choices=[1, 2])

        with self.assertRaises(ValueError) as context:
            Test(ConfigFactory.parse_string('i = 3'))
        self.assertEqual('"i" Illegal choice (3 not in [1, 2])', str(context.exception))
        Test.i.choices.append(3)
        self.assertEqual(Test(ConfigFactory.parse_string('i = 3')).i, 3)


class TestOptionalParameters(TestCase):
    def test_general(self):
        class Test(Configurable):
            p = Integer(default=1)
        self.assertTrue(Test.p.optional)
        self.assertEqual(Test(None).p, 1)
        self.assertEqual(Test(ConfigFactory.parse_string('missing { p = 1 }')).p, 1)

        class Test(Configurable):
            p1 = Integer(default=None)
            p2 = Integer(optional=True)
        self.assertFalse(Test.p1.optional)
        self.assertTrue(Test.p2.optional)

        with self.assertRaises(ConfigMissingException):
            Test(ConfigFactory.parse_string('p2 = 1'))
        self.assertEqual(Test(ConfigFactory.parse_string('p1 = 1')).p2, None)

        class Test(Configurable):
            p = Integer()
        self.assertFalse(Test.p.optional)
        with self.assertRaises(ConfigMissingException) as context:
            Test(ConfigFactory.parse_string('missing { p = 1 }'))
        self.assertEqual("'No configuration setting found for key p'", str(context.exception))


class TestFallbackGroups(TestCase):
    def test_general(self):
        class Test(Configurable):
            p1 = Integer().fallback(Integer('p2'))
        self.assertEqual(Test.p1.field_name, 'p1')
        self.assertEqual(Test(ConfigFactory.parse_string('p1 = 1')).p1, 1)
        self.assertEqual(Test(ConfigFactory.parse_string('p2 = 2')).p1, 2)

    def test_from_or(self):
        class Test(Configurable):
            p1 = Integer('p1') | Integer('p2') | Integer('p3')
        self.assertEqual(Test.p1.field_name, 'p1')
        self.assertEqual(Test(ConfigFactory.parse_string('p1 = 1')).p1, 1)
        self.assertEqual(Test(ConfigFactory.parse_string('p2 = 2')).p1, 2)
        self.assertEqual(Test(ConfigFactory.parse_string('p3 = 3')).p1, 3)

    def test_missing(self):
        class Test(Configurable):
            p1 = Integer('p1') | Integer('p2')
        self.assertIsInstance(Test.p1, FallbackGroup)
        self.assertEqual(Test.p1.field_name, 'p1')
        with self.assertRaises(ConfigMissingException):
            Test(ConfigFactory.parse_string('p3 = 3'))


class TestPhysicalParameters(TestCase):
    def test_general(self):
        class Test(Configurable):
            p = PhysicalQuantity(unit='mm')
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [mm]"')).p, 1.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [cm]"')).p, 10.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [m]"')).p, 1000.)

    def test_alternative_declaration(self):
        class Test(Configurable):
            p = PhysicalQuantity(unit=units.mm)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [mm]"')).p, 1.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [cm]"')).p, 10.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [m]"')).p, 1000.)

        class Test(Configurable):
            p = PhysicalQuantity(unit=units['mm'])
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [mm]"')).p, 1.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [cm]"')).p, 10.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [m]"')).p, 1000.)

    def test_changing_units(self):
        class Test(Configurable):
            p = PhysicalQuantity(unit=units.m)
        Test.p.unit = units.mm
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [mm]"')).p, 1.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [cm]"')).p, 10.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [m]"')).p, 1000.)
        Test.p.unit = 'mm'
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [mm]"')).p, 1.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [cm]"')).p, 10.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [m]"')).p, 1000.)

    def test_numericalunits_engine(self):
        units.engine = NumericalUnits
        self.assertIsInstance(units.engine, NumericalUnits)

        class Test(Configurable):
            p = PhysicalQuantity(unit='mm')
        # We need to use `self.assertAlmostEqual` here because the numericalunits package randomly
        # initializes each dimension with a numerical value and scales the corresponding units
        # with the required factors. Therefore if we do for example the conversion m -> mm then
        # what happens in fact is `(x * 1000) / x` with `x` a random number. Note the parentheses
        # which indicate that scaling of the single units happens first and conversion later on.
        # For some numbers `x` the conversion might not exactly yield the initial scaling factor.
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [mm]"')).p, 1.)
        self.assertAlmostEqual(Test(ConfigFactory.parse_string('p = "1 [cm]"')).p, 10., delta=2e-14)
        self.assertAlmostEqual(Test(ConfigFactory.parse_string('p = "1 [m]"')).p, 1000., delta=2e-12)

        class Test(Configurable):
            p = PhysicalQuantity(unit=units.mm)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [mm]"')).p, 1.)
        self.assertAlmostEqual(Test(ConfigFactory.parse_string('p = "1 [cm]"')).p, 10., delta=2e-14)
        self.assertAlmostEqual(Test(ConfigFactory.parse_string('p = "1 [m]"')).p, 1000., delta=2e-12)

        units.engine = Pint

    def test_units_engine(self):
        units.engine = Units
        self.assertIsInstance(units.engine, Units)

        class Test(Configurable):
            p = PhysicalQuantity(unit='mm')
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [mm]"')).p, 1.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [cm]"')).p, 10.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [m]"')).p, 1000.)

        class Test(Configurable):
            p = PhysicalQuantity(unit=units.mm)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [mm]"')).p, 1.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [cm]"')).p, 10.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 [m]"')).p, 1000.)

        units.engine = Pint


class TestFormulas(TestCase):
    def test_integers(self):
        class Test(Configurable):
            p = Integer()
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 + 2"')).p, 3)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "2*3"')).p, 6)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "2 ** 3"')).p, 8)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "(1 + 2)**3"')).p, 27)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "16 // 2"')).p, 8)
        with self.assertRaises(ValueError):
            Test(ConfigFactory.parse_string('p = "16 / 2"'))
        with self.assertRaises(ValueError):
            Test(ConfigFactory.parse_string('p = "2 * pi"'))
        with self.assertRaises(ValueError):
            Test(ConfigFactory.parse_string('p = "[1, 2, 3]"'))

    def test_numbers(self):
        class Test(Configurable):
            p = Number()
        self.assertEqual(Test(ConfigFactory.parse_string('p = "1 + 2"')).p, 3.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "2*3"')).p, 6.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "2 ** 3"')).p, 8.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "(1 + 2)**3"')).p, 27.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "16 / 2"')).p, 8.)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "2 * pi"')).p, 2. * np.pi)
        self.assertEqual(Test(ConfigFactory.parse_string('p = "2 * sin(pi/2)"')).p,
                         2. * np.sin(np.pi/2))

    def test_physical_quantities(self):
        class Test(Configurable):
            p = PhysicalQuantity(unit='kg')
        self.assertEqual(
            Test(ConfigFactory.parse_string('p = "2 * {electron mass} [kg]"')).p,
            2. * physical_constants['electron mass'][0]
        )

        class Test(Configurable):
            p = PhysicalQuantity(unit='eV / K')
        self.assertEqual(
            Test(ConfigFactory.parse_string('p = "{Boltzmann constant in eV/K} [eV/K]"')).p,
            physical_constants['Boltzmann constant in eV/K'][0]
        )

        class Test(Configurable):
            p = PhysicalQuantity(unit='1 / m**3')
        self.assertEqual(
            Test(ConfigFactory.parse_string('p = "{Loschmidt constant (273.15 K, 100 kPa)} [1/m^3]"')).p,
            physical_constants['Loschmidt constant (273.15 K, 100 kPa)'][0]
        )

    def test_deactivating_formulas(self):
        class Test(Configurable):
            p = PhysicalQuantity(unit='kg', formulas=True)
        self.assertEqual(
            Test(ConfigFactory.parse_string('p = "{electron mass} [kg]"')).p,
            physical_constants['electron mass'][0]
        )

        class Test(Configurable):
            p = PhysicalQuantity(unit='kg', formulas=False)
        with self.assertRaises(ValueError):
            Test(ConfigFactory.parse_string('p = "{electron mass} [kg]"'))


class TestComplementaryGroups(TestCase):
    def test_general(self):
        class Test(Configurable):
            g = ComplementaryGroup(
                (Integer('width'), lambda height, area: area // height),
                (Integer('height'), lambda width, area: area // width),
                (Integer('area'), lambda width, height: width * height)
            )
        self.assertEqual(Test.g.field_name, 'g')
        self.assertEqual(
            Test(ConfigFactory.parse_string('width = 2\nheight=3')).g,
            {'width': 2, 'height': 3, 'area': 6}
        )
        self.assertEqual(
            Test(ConfigFactory.parse_string('width = 2\narea=6')).g,
            {'width': 2, 'height': 3, 'area': 6}
        )
        self.assertEqual(
            Test(ConfigFactory.parse_string('area = 6\nheight=3')).g,
            {'width': 2, 'height': 3, 'area': 6}
        )


class TestAutocompleteParameterNames(TestCase):
    @classmethod
    def setUpClass(cls):
        from hanna.addons import AutocompleteParameterNames
        AutocompleteParameterNames.install()
        cls.AddOn = AutocompleteParameterNames

    @classmethod
    def tearDownClass(cls):
        cls.AddOn.uninstall()

    def test_general(self):
        from hanna import Configurable, Integer, String

        class Test(Configurable):
            foo = String()
        i = Integer()
        Test.bar = i
        self.assertEqual(Test.foo.name, 'foo')
        self.assertEqual(Test.bar.name, 'bar')
        self.assertEqual(i.name, None)

    def test_install_uninstall(self):
        self.AddOn.uninstall()
        from hanna import Configurable, String

        class Test(Configurable):
            pass
        Test.foo = String()
        self.assertEqual(Test.foo.name, None)

        self.AddOn.install()
        from hanna import Configurable, String

        class Test(Configurable):
            pass
        Test.bar = String()
        self.assertEqual(Test.bar.name, 'bar')

    def test_class_wide_sections(self):
        from hanna import Configurable, Integer, String

        class Test(Configurable, path='section'):
            foo = String()
        Test.bar = Integer()
        self.assertEqual(Test.foo.name, 'section.foo')
        self.assertEqual(Test.bar.name, 'section.bar')


if __name__ == '__main__':
    unittest.main()
