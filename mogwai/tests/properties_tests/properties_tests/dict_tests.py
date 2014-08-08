from __future__ import unicode_literals
from nose.plugins.attrib import attr
from .base_tests import GraphPropertyBaseClassTestCase
from mogwai.properties.properties import Dictionary
from mogwai.models import Vertex
from mogwai._compat import print_


@attr('unit', 'property', 'property_dict')
class DictionaryPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Dictionary
    good_cases = ({}, {'test': 1}, None)
    bad_cases = (0, 1.1, 'val', ['val'])


class DictionaryTestVertex(Vertex):
    element_type = 'test_dictionary_vertex'

    test_val = Dictionary()


@attr('unit', 'property', 'property_dict')
class DictionaryVertexTestCase(GraphPropertyBaseClassTestCase):

    def test_dictionary_io(self):
        print_("creating vertex")
        dt = DictionaryTestVertex.create(test_val={'test': 1})
        print_("getting vertex from vertex: %s" % dt)
        dt2 = DictionaryTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        dt2.delete()

        dt = DictionaryTestVertex.create(test_val={'test2': 2})
        print_("\ncreated vertex: %s" % dt)
        dt2 = DictionaryTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, {'test2': 2})
        print_("deleting vertex")
        dt2.delete()