from __future__ import unicode_literals
from nose.plugins.attrib import attr
from base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import Integer, Short, PositiveInteger
from mogwai.models import Vertex
from mogwai._compat import print_


@attr('unit', 'property', 'property_int')
class IntegerPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Integer
    good_cases = (1, 0)
    bad_cases = ('', 'a', 1.1, None, [], [1], {}, {'a': 1})


class IntegerTestVertex(Vertex):
    element_type = 'test_integer_vertex'

    test_val = Integer()


@attr('unit', 'property', 'property_int')
class IntegerVertexTestCase(GraphPropertyBaseClassTestCase):

    def test_integer_io(self):
        print_("creating vertex")
        dt = IntegerTestVertex.create(test_val=1)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = IntegerTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = IntegerTestVertex.create(test_val=2)
        print_("\ncreated vertex: %s" % dt)
        dt2 = IntegerTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 2)
        print_("deleting vertex")
        dt2.delete()


@attr('unit', 'property', 'property_short')
class ShortPropertyTestCase(IntegerPropertyTestCase):
    klass = Short


class ShortTestVertex(Vertex):
    element_type = 'test_short_vertex'

    test_val = Short()


@attr('unit', 'property', 'property_short')
class ShortVertexTestCase(GraphPropertyBaseClassTestCase):

    def test_short_io(self):
        print_("creating vertex")
        dt = ShortTestVertex.create(test_val=1)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = ShortTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = ShortTestVertex.create(test_val=2)
        print_("\ncreated vertex: %s" % dt)
        dt2 = ShortTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 2)
        print_("deleting vertex")
        dt2.delete()


@attr('unit', 'property', 'property_posint')
class PositiveIntegerPropertyTestCase(IntegerPropertyTestCase):
    klass = PositiveInteger


class PositiveIntegerTestVertex(Vertex):
    element_type = 'test_positive_integer_vertex'

    test_val = PositiveInteger()


@attr('unit', 'property', 'property_posint')
class PositiveIntegerVertexTestCase(GraphPropertyBaseClassTestCase):

    def test_positive_integer_io(self):
        print_("creating vertex")
        dt = PositiveIntegerTestVertex.create(test_val=1)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = PositiveIntegerTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = PositiveIntegerTestVertex.create(test_val=2)
        print_("\ncreated vertex: %s" % dt)
        dt2 = PositiveIntegerTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 2)
        print_("deleting vertex")
        dt2.delete()