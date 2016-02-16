from __future__ import unicode_literals
from nose.plugins.attrib import attr

from tornado.testing import gen_test
from .base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import Slug
from mogwai.models import Vertex
from mogwai._compat import print_


@attr('unit', 'property', 'property_slug')
class SlugPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Slug
    good_cases = ('ab', '12', 'ab12', '12ab', None)
    bad_cases = ('@', 'a!', '12!', 'ab12!', 0, 1.1, [], (), {})

    def test_slug_defaults(self):
        p = Slug(default='ab')


class SlugTestVertex(Vertex):
    element_type = 'test_slug_vertex'

    test_val = Slug()


@attr('unit', 'property', 'property_slug')
class SlugVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_slug_io(self):
        print_("creating vertex")
        dt = yield SlugTestVertex.create(test_val='ab12')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield SlugTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield SlugTestVertex.create(test_val='12ab')
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield SlugTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, '12ab')
        print_("deleting vertex")
        yield dt2.delete()
