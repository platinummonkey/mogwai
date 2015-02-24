from __future__ import unicode_literals
from unittest import TestCase
from nose.tools import nottest
from mogwai.connection import setup, sync_spec
from mogwai.models import Vertex, Edge
from mogwai.properties import Double, Integer, String
import os

_val = 0


def counter():
    global _val
    _val += 1
    return _val


class TestVertexModel(Vertex):
    element_type = 'test_vertex_model'

    name = String(default='test_vertex')
    test_val = Integer(default=counter)


class TestVertexModelDouble(Vertex):
    element_type = 'test_vertex_model_double'

    name = String(default='test_vertex_double')
    test_val = Double(default=0.0)


class TestEdgeModel(Edge):
    label = 'test_edge_model'

    name = String(default='test_edge')
    test_val = Integer(default=counter)


class TestEdgeModel2(Edge):
    label = 'test_edge_model_2'

    name = String(default='test_edge')
    test_val = Integer(default=counter)


class TestEdgeModelDouble(Edge):
    label = 'test_edge_model_double'

    name = String(default='test_edge_double')
    test_val = Double(default=0.0)


@nottest
def testcase_docstring_sub(*sub):
    """ If you wanted to lazy load something into a docstring on a test.

    Do not use this normally, it's bad practice.
    """
    def decorated(obj):
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj
    return decorated


class BaseMogwaiTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseMogwaiTestCase, cls).setUpClass()
        #sync_spec(filename='test.spec', host='192.168.133.12', graph_name='graph')
        setup(os.getenv('TITAN_REXPRO_URL', 'localhost'), graph_name='graph')

    def assertHasAttr(self, obj, attr):
        self.assertTrue(hasattr(obj, attr), "%s doesn't have attribute: %s" % (obj, attr))

    def assertNotHasAttr(self, obj, attr):
        self.assertFalse(hasattr(obj, attr), "%s shouldn't have attribute: %s" % (obj, attr))

    def assertAttrEqual(self, obj, attr, value):
        self.assertHasAttr(obj, attr)
        self.assertEqual(getattr(obj, attr), value)

    def assertAttrNotEqual(self, obj, attr, value):
        self.assertHasAttr(obj, attr)
        self.assertNotEqual(getattr(obj, attr), value)

    def assertNotRaise(self, callableObj, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except Exception as e:
            raise AssertionError("Shouldn't raise and exception: {}".format(e))

    def assertAnyRaise(self, callableObj, *args, **kwargs):
        try:
            callableObj(*args, **kwargs)
        except:
            return
        raise AssertionError("Should raise an exception")

    def assertIsSubclass(self, C, B):
        if issubclass(C, B):
            return
        else:
            raise AssertionError("{} is Not a Subclass of {}".format(B, C))

    def assertDictContainsKey(self, obj, key):
        if key in obj:
            return
        else:
            raise AssertionError("{} is not in dict: {}".format(key, obj))

    def assertDictContainsKeyWithValueType(self, obj, key, B):
        if key in obj:
            if isinstance(obj[key], B):
                return
            else:
                raise AssertionError("dict[{}]={} is not of type: {}".format(key, obj[key], B))
        else:
            raise AssertionError("{} is not in dict: {}".format(key, obj))

    def assertIsVertex(self, obj):
        self.assertIsSubclass(obj, Vertex)

    def assertIsEdge(self, obj):
        self.assertIsSubclass(obj, Edge)
