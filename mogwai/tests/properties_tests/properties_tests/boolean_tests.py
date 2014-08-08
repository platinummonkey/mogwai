from __future__ import unicode_literals
from nose.plugins.attrib import attr
from mogwai.tests import BaseMogwaiTestCase
from .base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import Boolean, GraphProperty
from mogwai.models import Vertex
from mogwai.exceptions import ValidationError
from mogwai._compat import print_


@attr('unit', 'property', 'property_boolean')
class BooleanPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Boolean
    good_cases = (True, False, None)
    bad_cases = (0, 1.1, 'val', [], (), {})


class BooleanTestVertex(Vertex):
    element_type = 'test_boolean_vertex'

    test_val = Boolean()

CHOICES = (
    (True, True),
    (False, False)
)


class BooleanTestChoicesVertex(Vertex):
    element_type = 'test_boolean_choices_vertex'

    test_val = Boolean(choices=CHOICES)


@attr('unit', 'property', 'property_boolean')
class BooleanVertexTestCase(GraphPropertyBaseClassTestCase):

    def test_boolean_io(self):
        print_("creating vertex")
        dt = BooleanTestVertex.create(test_val=True)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = BooleanTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = BooleanTestVertex.create(test_val=True)
        print_("\ncreated vertex: %s" % dt)
        dt2 = BooleanTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, True)
        print_("deleting vertex")
        dt2.delete()


@attr('unit', 'property', 'property_boolean')
class TestVertexChoicesTestCase(BaseMogwaiTestCase):

    def test_good_choices_value_io(self):
        print_("creating vertex")
        dt = BooleanTestChoicesVertex.create(test_val=True)
        print_("validating input")
        self.assertEqual(dt.test_val, True)
        print_("deleting vertex")
        dt.delete()

    def test_good_choices_key_io(self):
        print_("creating vertex")
        dt = BooleanTestChoicesVertex.create(test_val=False)
        print_("validating input")
        self.assertEqual(dt.test_val, False)
        print_("deleting vertex")
        dt.delete()

    def test_bad_choices_io(self):
        with self.assertRaises(ValidationError):
            print_("creating vertex")
            dt = BooleanTestChoicesVertex.create(test_val=None)
            print_("validating input")
            self.assertEqual(dt.test_val, None)
            print_("deleting vertex")
            dt.delete()