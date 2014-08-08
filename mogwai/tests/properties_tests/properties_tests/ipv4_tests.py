from __future__ import unicode_literals
from nose.plugins.attrib import attr
from .base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import IPV4
from mogwai.models import Vertex
from mogwai._compat import print_


@attr('unit', 'property', 'property_ipv4')
class IPV4PropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = IPV4
    good_cases = ('1.2.3.4', '0.0.0.0', '255.255.255.255')
    bad_cases = ('0', '0.', '0.0', '0.0.', '0.0.0', '0.0.0.', '256.256.256.256', '1.2.3.256')

    def test_ipv4_default_cases(self):
        p = IPV4(default='1.2.3.4')


class IPV4TestVertex(Vertex):
    element_type = 'test_ipv4_vertex'

    test_val = IPV4()


@attr('unit', 'property', 'property_ipv4')
class IPV4VertexTestCase(GraphPropertyBaseClassTestCase):

    def test_ipv4_io(self):
        print_("creating vertex")
        dt = IPV4TestVertex.create(test_val='1.2.3.4')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = IPV4TestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = IPV4TestVertex.create(test_val='4.3.2.1')
        print_("\ncreated vertex: %s" % dt)
        dt2 = IPV4TestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, '4.3.2.1')
        print_("deleting vertex")
        dt2.delete()