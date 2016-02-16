from __future__ import unicode_literals
from nose.plugins.attrib import attr

from tornado.testing import gen_test

from .base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import Integer, Short, PositiveInteger, Long, PositiveLong
from mogwai.models import Vertex
from mogwai._compat import print_, long_


@attr('unit', 'property', 'property_int')
class IntegerPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Integer
    good_cases = (1, 0, None)
    bad_cases = ('', 'a', 1.1, [], [1], {}, {'a': 1})


class IntegerTestVertex(Vertex):
    element_type = 'test_integer_vertex'

    test_val = Integer()


@attr('unit', 'property', 'property_int')
class IntegerVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_integer_io(self):
        print_("creating vertex")
        dt = yield IntegerTestVertex.create(test_val=1)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield IntegerTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield IntegerTestVertex.create(test_val=2)
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield IntegerTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 2)
        print_("deleting vertex")
        yield dt2.delete()


@attr('unit', 'property', 'property_long')
class LongPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Long
    good_cases = (long_(1), long_(0), None)
    bad_cases = ('', 'a', 1.1, [], [1], {}, {'a': 1})


class LongTestVertex(Vertex):
    element_type = 'test_long_vertex'

    test_val = Long()


@attr('unit', 'property', 'property_long')
class LongVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_long_io(self):
        print_("creating vertex")
        dt = yield LongTestVertex.create(test_val=1)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield LongTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield LongTestVertex.create(test_val=2)
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield LongTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 2)
        print_("deleting vertex")
        yield dt2.delete()


@attr('unit', 'property', 'property_short')
class ShortPropertyTestCase(IntegerPropertyTestCase):
    klass = Short


class ShortTestVertex(Vertex):
    element_type = 'test_short_vertex'

    test_val = Short()


@attr('unit', 'property', 'property_short')
class ShortVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_short_io(self):
        print_("creating vertex")
        dt = yield ShortTestVertex.create(test_val=1)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield ShortTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield ShortTestVertex.create(test_val=2)
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield ShortTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 2)
        print_("deleting vertex")
        yield dt2.delete()


@attr('unit', 'property', 'property_posint')
class PositiveIntegerPropertyTestCase(IntegerPropertyTestCase):
    klass = PositiveInteger


class PositiveIntegerTestVertex(Vertex):
    element_type = 'test_positive_integer_vertex'

    test_val = PositiveInteger()


@attr('unit', 'property', 'property_posint')
class PositiveIntegerVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_positive_integer_io(self):
        print_("creating vertex")
        dt = yield PositiveIntegerTestVertex.create(test_val=1)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield PositiveIntegerTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield PositiveIntegerTestVertex.create(test_val=2)
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield PositiveIntegerTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 2)
        print_("deleting vertex")
        yield dt2.delete()


@attr('unit', 'property', 'property_poslong')
class PositiveLongPropertyTestCase(LongPropertyTestCase):
    klass = PositiveLong


class PositiveLongTestVertex(Vertex):
    element_type = 'test_positive_long_vertex'

    test_val = PositiveLong()


@attr('unit', 'property', 'property_poslong')
class PositiveLongVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_positive_long_io(self):
        print_("creating vertex")
        dt = yield PositiveLongTestVertex.create(test_val=1)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield PositiveLongTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield PositiveLongTestVertex.create(test_val=2)
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield PositiveLongTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 2)
        print_("deleting vertex")
        yield dt2.delete()
