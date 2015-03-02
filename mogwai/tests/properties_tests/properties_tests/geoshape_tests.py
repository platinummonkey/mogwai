from __future__ import unicode_literals
from nose.plugins.attrib import attr
from .base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import GeoShape, GeoShapeObject
from mogwai.models import Vertex
from mogwai._compat import print_


@attr('unit', 'property', 'property_geoshape')
class GeoShapePropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = GeoShape
    good_cases = (GeoShapeObject.point(0.0, 1.0),
                  GeoShapeObject.box(0.0, 1.0, 2.0, 3.0),
                  GeoShapeObject.circle(0.0, 1.0, 2.0),
                  None)
    bad_cases = ('ab12!', 0, 1.1, [], (), {})

    def test_slug_defaults(self):
        p = GeoShape(default=GeoShapeObject.point(0.0, 0.0))


class GeoShapeTestVertex(Vertex):
    element_type = 'test_geoshape_vertex'

    test_val = GeoShape()


@attr('unit', 'property', 'property_geoshape')
class GeoShapeVertexTestCase(GraphPropertyBaseClassTestCase):

    def test_geoshape_io(self):
        """ Test GeoShape property I/O"""
        # point type
        print_("creating vertex")
        dt = GeoShapeTestVertex.create(test_val=GeoShapeObject.point(0.0, 1.0))
        print_("getting vertex from vertex: %s" % dt)
        dt2 = GeoShapeTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        # box type
        dt = GeoShapeTestVertex.create(test_val=GeoShapeObject.box(0.0, 1.0, 2.0, 3.0))
        print_("\ncreated vertex: %s" % dt)
        dt2 = GeoShapeTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, GeoShapeObject.box(0.0, 1.0, 2.0, 3.0))
        print_("deleting vertex")
        dt2.delete()

        # circle type
        dt = GeoShapeTestVertex.create(test_val=GeoShapeObject.circle(0.0, 1.0, 2.0))
        print_("\ncreated vertex: %s" % dt)
        dt2 = GeoShapeTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, GeoShapeObject.circle(0.0, 1.0, 2.0))
        print_("deleting vertex")
        dt2.delete()
