from __future__ import unicode_literals
from nose.plugins.attrib import attr

from tornado.testing import gen_test
from .base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import Email
from mogwai.models import Vertex
from mogwai._compat import print_


@attr('unit', 'property', 'property_email')
class EmailPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Email
    good_cases = ('test@test.com', 'test-alice@subdomain.domain.com')
    bad_cases = ('', 'bob', '@test.com', 'bob@test')

    def test_email_edge_cases(self):
        p = Email(default='bob@bob.net')


class EmailTestVertex(Vertex):
    element_type = 'test_email_vertex'

    test_val = Email()


@attr('unit', 'property', 'property_email')
class EmailVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_email_io(self):
        print_("creating vertex")
        dt = yield EmailTestVertex.create(test_val='alice@alice.com')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield EmailTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield EmailTestVertex.create(test_val='bob@bob.com')
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield EmailTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 'bob@bob.com')
        print_("deleting vertex")
        yield dt2.delete()
