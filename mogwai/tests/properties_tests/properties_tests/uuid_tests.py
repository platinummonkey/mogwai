from __future__ import unicode_literals
from nose.plugins.attrib import attr
from .base_tests import GraphPropertyBaseClassTestCase
from mogwai._compat import PY2
from mogwai.properties.properties import UUID
from mogwai.properties.base import GraphProperty, ValidationError
from mogwai.models import Vertex
from mogwai._compat import print_


@attr('unit', 'property', 'property_uuid')
class UUID4PropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = UUID
    good_cases = ('bb19eaed-c946-4cef-8001-7cc3357cc439', None)
    if PY2:
        bad_cases = ('val', [], (), {}, 0, long(1), False, 1.1)
    else:
        bad_cases = ('val', [], (), {}, 0, False, 1.1)

    def test_to_database_method(self):
        u = self.klass(default=None)
        self.assertIsNone(u.to_database(None))


class UUID4TestVertex(Vertex):
    element_type = 'test_uuid4_vertex'

    test_val = UUID()


@attr('unit', 'property', 'property_uuid')
class UUID4VertexTestCase(GraphPropertyBaseClassTestCase):

    def test_uuid4_io(self):
        print_("creating vertex")
        dt = UUID4TestVertex.create(test_val='bb19eaed-c946-4cef-8001-7cc3357cc439')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = UUID4TestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = UUID4TestVertex.create(test_val='bb19eaed-c946-4cef-8001-7cc3357cc439')
        print_("\ncreated vertex: %s" % dt)
        dt2 = UUID4TestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 'bb19eaed-c946-4cef-8001-7cc3357cc439')
        print_("deleting vertex")
        dt2.delete()


@attr('unit', 'property', 'property_uuid')
class UUID1PropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = UUID(version='uuid1')
    good_cases = ('bb19eaed-c946-4cef-8001-7cc3357cc439', None)
    if PY2:
        bad_cases = ('val', [], (), {}, 0, long(1), False, 1.1)
    else:
        bad_cases = ('val', [], (), {}, 0, False, 1.1)

    def test_subclass(self):
        """ Test if Property is a GraphProperty """
        self.assertIsSubclass(self.klass.__class__, GraphProperty)

    def test_validation(self):
        for case in self.good_cases:
            print_("testing good case: %s" % (case, ))
            self.assertNotRaise(self.klass.validate, case)

        for case in self.bad_cases:
            print_("testing bad case: %s" % (case, ))
            self.assertRaises(ValidationError, self.klass.validate, case)


class UUID1TestVertex(Vertex):
    element_type = 'test_uuid1_vertex'

    test_val = UUID(version='uuid1')


@attr('unit', 'property', 'property_uuid')
class UUID1VertexTestCase(GraphPropertyBaseClassTestCase):

    def test_uuid1_io(self):
        print_("creating vertex")
        dt = UUID1TestVertex.create(test_val='bb19eaed-c946-4cef-8001-7cc3357cc439')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = UUID1TestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = UUID1TestVertex.create(test_val='bb19eaed-c946-4cef-8001-7cc3357cc439')
        print_("\ncreated vertex: %s" % dt)
        dt2 = UUID1TestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 'bb19eaed-c946-4cef-8001-7cc3357cc439')
        print_("deleting vertex")
        dt2.delete()