from __future__ import unicode_literals
from mogwai._compat import print_
from six import string_types
from nose.plugins.attrib import attr
from nose.tools import nottest


from .base import BaseMogwaiTestCase
from mogwai.connection import generate_spec, execute_query
from mogwai.models import Vertex, Edge
from mogwai.properties import String
from mogwai.spec import get_existing_indices


class TestIndexSpecVertex(Vertex):
    element_type = 'test_index_spec_vertex_model'

    name = String(default='test_vertex', index=True, index_ext='es')


class TestIndexSpecEdge(Edge):
    label = 'test_index_spec_edge_model'

    name = String(default='test_edge', index=True, index_ext='es')


@attr('unit', 'connection')
class TestSpecSystem(BaseMogwaiTestCase):
    """ Test specification system """

    def test_loaded(self):
        spec = generate_spec()
        self.assertIsInstance(spec, (list, tuple))
        self.assertGreater(len(spec), 0)
        for s in spec:
            print_(s)
            self.assertIsInstance(s, dict)
            self.assertDictContainsKeyWithValueType(s, 'model', string_types)
            self.assertDictContainsKeyWithValueType(s, 'element_type', string_types)
            self.assertDictContainsKeyWithValueType(s, 'makeType', string_types)
            self.assertDictContainsKeyWithValueType(s, 'properties', dict)
            for pk, pv in s['properties'].items():
                self.assertDictContainsKeyWithValueType(pv, 'data_type', string_types)
                self.assertDictContainsKeyWithValueType(pv, 'index_ext', string_types)
                self.assertDictContainsKeyWithValueType(pv, 'uniqueness', string_types)
                self.assertDictContainsKeyWithValueType(pv, 'compiled', dict)
                self.assertDictContainsKeyWithValueType(pv['compiled'], 'script', string_types)
                self.assertDictContainsKeyWithValueType(pv['compiled'], 'params', dict)
                self.assertDictContainsKeyWithValueType(pv['compiled'], 'transaction', bool)

    @nottest
    def test_gather_existing_indices(self):
        """ Make sure existing indices can be gathered """
        v_idx, e_idx = get_existing_indices()
        self.assertEqual(len(v_idx), 0)
        self.assertEqual(len(e_idx), 0)

        # create vertex and edge index
        execute_query('g.makeKey(name).dataType(Object.class).indexed(Vertex.class).make(); g.commit()',
                      params={'name': 'testvertexindex'})
        execute_query('g.makeLabel(name).dataType(Object.class).indexed(Edge.class).make(); g.commit()',
                      params={'name': 'testedgeindex'})
        v_idx, e_idx = get_existing_indices()
        self.assertEqual(len(v_idx), 1)
        self.assertEqual(len(e_idx), 1)