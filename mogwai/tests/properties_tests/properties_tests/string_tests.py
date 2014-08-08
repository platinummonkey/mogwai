from __future__ import unicode_literals
from nose.plugins.attrib import attr
from mogwai.tests import BaseMogwaiTestCase
from .base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import String, Text, GraphProperty
from mogwai.models import Vertex
from mogwai.exceptions import ValidationError
from mogwai._compat import print_


@attr('unit', 'property', 'property_string')
class StringPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = String
    good_cases = ('test', None)
    bad_cases = (0, 1.1, [], (), {})

    def test_max_min_length_validation_error(self):
        s = self.klass(max_length=5, min_length=2)
        with self.assertRaises(ValidationError):
            s.validate('123456')
        with self.assertRaises(ValidationError):
            s.validate('1')


class StringTestVertex(Vertex):
    element_type = 'test_string_vertex'

    test_val = String()

CHOICES = (
    ('A', 1),
    ('B', 2)
)


class StringTestChoicesVertex(Vertex):
    element_type = 'test_string_choices_vertex'

    test_val = String(choices=CHOICES)


@attr('unit', 'property', 'property_string')
class StringVertexTestCase(GraphPropertyBaseClassTestCase):

    def test_string_io(self):
        print_("creating vertex")
        dt = StringTestVertex.create(test_val='test')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = StringTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = StringTestVertex.create(test_val='tset')
        print_("\ncreated vertex: %s" % dt)
        dt2 = StringTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 'tset')
        print_("deleting vertex")
        dt2.delete()


@attr('unit', 'property', 'property_string')
class TextPropertyTestCase(StringPropertyTestCase):
    klass = Text


class TextTestVertex(Vertex):
    element_type = 'test_text_vertex'

    test_val = Text()


@attr('unit', 'property', 'property_string')
class TextVertexTestCase(GraphPropertyBaseClassTestCase):

    def test_text_io(self):
        print_("creating vertex")
        dt = TextTestVertex.create(test_val='ab12')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = TextTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = TextTestVertex.create(test_val='12ab')
        print_("\ncreated vertex: %s" % dt)
        dt2 = TextTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, '12ab')
        print_("deleting vertex")
        dt2.delete()


@attr('unit', 'property', 'property_string')
class TestVertexChoicesTestCase(BaseMogwaiTestCase):

    def test_good_choices_value_io(self):
        print_("creating vertex")
        dt = StringTestChoicesVertex.create(test_val=1)
        print_("validating input")
        self.assertEqual(dt.test_val, 'A')
        print_("deleting vertex")
        dt.delete()

    def test_good_choices_key_io(self):
        print_("creating vertex")
        dt = StringTestChoicesVertex.create(test_val='B')
        print_("validating input")
        self.assertEqual(dt.test_val, 'B')
        print_("deleting vertex")
        dt.delete()

    def test_bad_choices_io(self):
        with self.assertRaises(ValidationError):
            print_("creating vertex")
            dt = StringTestChoicesVertex.create(test_val=3)
            print_("validating input")
            self.assertEqual(dt.test_val, 'C')
            print_("deleting vertex")
            dt.delete()