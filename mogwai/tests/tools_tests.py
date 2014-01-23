from __future__ import unicode_literals
from mogwai._compat import string_types, PY2
from nose.plugins.attrib import attr
from mogwai.tests import BaseMogwaiTestCase
from mogwai.models import Vertex, Edge
from mogwai import properties
from mogwai.tools import ImportStringError, import_string, cached_property, LazyImportClass, _Missing, Factory
import factory


@attr('unit', 'tools')
class TestImportString(BaseMogwaiTestCase):

    def test_raises_import_string_error(self):
        with self.assertRaises(ImportStringError):
            import_string('does.not.exist')
        with self.assertRaises(ImportStringError):
            import_string('does.not:exist')

    def test_imports_correctly(self):
        cp = import_string('mogwai.tools:cached_property')
        self.assertIs(cp, cached_property)

    def test_import_string_error_class(self):
        ise = ImportStringError('mogwai.tools.cached_property', 'Should work')


class LazyImportObject(object):
    pass


@attr('unit', 'tools')
class TestLazyImportString(BaseMogwaiTestCase):

    def test_lazy_import(self):
        li = LazyImportClass('mogwai.tools._Missing')
        self.assertIsInstance(li, LazyImportClass)
        self.assertIs(li.klass, _Missing)
        self.assertIsInstance(li(), _Missing)


class TestFactoryVertex(Vertex):
    element_type = 'test_factory_vertex'

    name = properties.String(required=True, max_length=128)


class TestFactoryVertexFactory(Factory):
    FACTORY_FOR = TestFactoryVertex

    name = factory.Sequence(lambda n: 'Test Factory Vertex {}'.format(n))


class TestFactoryEdge(Edge):
    label = 'test_factory_edge'

    name = properties.String(required=True, max_length=128)


class TestFactoryEdgeFactory(Factory):
    FACTORY_FOR = TestFactoryEdge

    name = factory.Sequence(lambda n: 'Test Factory Edge {}'.format(n))


@attr('unit', 'tools', 'factory')
class TestModelFactory(BaseMogwaiTestCase):

    def test_vertex_factory(self):
        v1 = TestFactoryVertexFactory()
        self.assertIsInstance(v1, TestFactoryVertex)
        self.assertTrue(v1.name.startswith('Test Factory Vertex'))
        v1.delete()
        v2 = TestFactoryVertexFactory.create()
        self.assertIsInstance(v2, TestFactoryVertex)
        self.assertTrue(v2.name.startswith('Test Factory Vertex'))
        v2.delete()

    def test_edge_factory(self):
        v1 = TestFactoryVertexFactory()
        v2 = TestFactoryVertexFactory()
        e1 = TestFactoryEdgeFactory(outV=v1, inV=v2)
        e2 = TestFactoryEdgeFactory.create(outV=v1, inV=v2)
        self.assertIsInstance(e1, TestFactoryEdge)
        self.assertTrue(e1.name.startswith('Test Factory Edge'))
        self.assertIsInstance(e2, TestFactoryEdge)
        self.assertTrue(e2.name.startswith('Test Factory Edge'))
        e1.delete()
        e2.delete()
        v1.delete()
        v2.delete()