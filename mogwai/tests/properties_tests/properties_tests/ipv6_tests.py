from __future__ import unicode_literals
from nose.plugins.attrib import attr
from .base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import IPV6, IPV6WithV4
from mogwai.models import Vertex
from mogwai._compat import print_


@attr('unit', 'property', 'property_ipv6')
class IPV6PropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = IPV6
    good_cases = ('1:2:3:4:5:6:7:8', '1::', '1:2:3:4:5:6:7::',
                  '1::8', '1:2:3:4:5:6::8', '1:2:3:4:5:6::8',
                  '1::7:8', '1:2:3:4:5::7:8', '1:2:3:4:5::8',
                  '1::6:7:8', '1:2:3:4::6:7:8', '1:2:3:4::8',
                  '1::5:6:7:8', '1:2:3::5:6:7:8', '1:2:3::8',
                  '1::4:5:6:7:8', '1:2::4:5:6:7:8', '1:2::8',
                  '1::3:4:5:6:7:8', '1::3:4:5:6:7:8', '1::8',
                  '::2:3:4:5:6:7:8', '::2:3:4:5:6:7:8', '::8', '::')
    bad_cases = ('0', '0.', '0.0', '0.0.', '0.0.0', '0.0.0.', '256.256.256.256', '1.2.3.256')

    def test_ipv6_default_cases(self):
        p = IPV6(default='1:2:3:4:5:6:7:8')


class IPV6TestVertex(Vertex):
    element_type = 'test_ipv6_vertex'

    test_val = IPV6()


@attr('unit', 'property', 'property_ipv6')
class IPV6VertexTestCase(GraphPropertyBaseClassTestCase):

    def test_ipv6_io(self):
        print_("creating vertex")
        dt = IPV6TestVertex.create(test_val='1::8')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = IPV6TestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = IPV6TestVertex.create(test_val='1::7:8')
        print_("\ncreated vertex: %s" % dt)
        dt2 = IPV6TestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, '1::7:8')
        print_("deleting vertex")
        dt2.delete()


@attr('unit', 'property', 'property_ipv6w4')
class IPV6WithV4PropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = IPV6WithV4
    good_cases = ('1:2:3:4:5:6:7:8', '1::', '1:2:3:4:5:6:7::',  # IPv6
                  '1::8', '1:2:3:4:5:6::8', '1:2:3:4:5:6::8',
                  '1::7:8', '1:2:3:4:5::7:8', '1:2:3:4:5::8',
                  '1::6:7:8', '1:2:3:4::6:7:8', '1:2:3:4::8',
                  '1::5:6:7:8', '1:2:3::5:6:7:8', '1:2:3::8',
                  '1::4:5:6:7:8', '1:2::4:5:6:7:8', '1:2::8',
                  '1::3:4:5:6:7:8', '1::3:4:5:6:7:8', '1::8',
                  '::2:3:4:5:6:7:8', '::2:3:4:5:6:7:8', '::8', '::',
                  '::255.255.255.255', '::ffff:255.255.255.255', '::ffff:0:255.255.255.255',  # Mapped/Translated
                  '2001:db8:3:4::192.0.2.33', '64:ff9b::192.0.2.33',  # Embedded
                  )
    bad_cases = ('0', '0.', '0.0', '0.0.', '0.0.0', '0.0.0.', '256.256.256.256', '1.2.3.256', '1.2.3.4')

    def test_ipv6_default_cases(self):
        p = IPV6WithV4(default='1:2:3:4:5:6:7:8')


class IPV64TestVertex(Vertex):
    element_type = 'test_ipv64_vertex'

    test_val = IPV6WithV4()


@attr('unit', 'property', 'property_ipv6w4')
class IPV64VertexTestCase(GraphPropertyBaseClassTestCase):

    def test_ipv64_io(self):
        print_("creating vertex")
        dt = IPV64TestVertex.create(test_val='::255.255.255.255')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = IPV64TestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = IPV64TestVertex.create(test_val='::ffff:255.255.255.255')
        print_("\ncreated vertex: %s" % dt)
        dt2 = IPV64TestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, '::ffff:255.255.255.255')
        print_("deleting vertex")
        dt2.delete()