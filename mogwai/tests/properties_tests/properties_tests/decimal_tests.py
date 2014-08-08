from __future__ import unicode_literals
from nose.plugins.attrib import attr
from .base_tests import GraphPropertyBaseClassTestCase
from decimal import Decimal as _D
from mogwai.properties.properties import Decimal
from mogwai.models import Vertex
from mogwai._compat import print_


@attr('unit', 'property', 'property_decimal')
class DecimalPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Decimal
    good_cases = (1.1, 0.0, _D(1.1), None)
    bad_cases = (0, 'val', ['val'], {'val': 1})


class DecimalTestVertex(Vertex):
    element_type = 'test_decimal_vertex'

    test_val = Decimal()


@attr('unit', 'property', 'property_decimal')
class DecimalVertexTestCase(GraphPropertyBaseClassTestCase):

    def test_decimal_io(self):
        print_("creating vertex")
        dt = DecimalTestVertex.create(test_val=_D('1.00'))
        print_("getting vertex from vertex: %s" % dt)
        dt2 = DecimalTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = DecimalTestVertex.create(test_val=5)
        print_("\ncreated vertex: %s" % dt)
        dt2 = DecimalTestVertex.get(dt._id)
        print_("Got decimal vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, _D('5'))
        print_("deleting vertex")
        dt2.delete()
