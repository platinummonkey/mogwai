from __future__ import unicode_literals
from nose.plugins.attrib import attr
from mogwai.models import Vertex, Edge
from mogwai.properties import String, Integer
from mogwai.exceptions import MogwaiRelationshipException
from mogwai.tests.base import BaseMogwaiTestCase, TestEdgeModel, TestVertexModel, counter
from mogwai.relationships.base import Relationship


class TestVertex2Model(Vertex):
    element_type = 'test_vertex2_model'

    name = String(default='test_vertex')
    test_val = Integer(default=counter)


class TestEdge2Model(Edge):
    label = 'test_edge2_model'

    name = String(default='test_edge')
    test_val = Integer(default=counter)


@attr('unit', 'relationship')
class GraphRelationshipBaseTestCase(BaseMogwaiTestCase):
    """ Test Relationship Functionality """

    @classmethod
    def setUpClass(cls):
        super(GraphRelationshipBaseTestCase, cls).setUpClass()
        cls.relationship_base_cls = Relationship
        cls.edge_model = TestEdgeModel
        cls.vertex_model = TestVertexModel
        cls.vertex_start = TestVertexModel.create(name='test relationship')

    @classmethod
    def tearDownClass(cls):
        cls.vertex_start.delete()
        super(GraphRelationshipBaseTestCase, cls).tearDownClass()

    def test_instantiation(self):
        """ Test that the Relationship is properly Instantiated """

        # setup relationship
        relationship = self.relationship_base_cls(self.edge_model, self.vertex_model)
        self.assertIsNone(relationship.top_level_vertex_class)
        self.assertIsNone(relationship.top_level_vertex)

        with self.assertRaises(MogwaiRelationshipException):
            relationship.create({}, {})

    def test_relationship_io(self):
        """ Test Relationship GraphDB interaction for querying Edges and Vertices """


        # setup relationship
        relationship = self.relationship_base_cls(self.edge_model, self.vertex_model)
        relationship.top_level_vertex = self.vertex_start
        relationship.top_level_vertex_class = self.vertex_model

        vertices = relationship.vertices()
        self.assertEqual(len(vertices), 0)

        v2 = self.vertex_model.create(name='other side relationship')
        e1 = self.edge_model.create(v2, self.vertex_start)

        vertices = relationship.vertices()
        self.assertEqual(len(vertices), 1)

        edges = relationship.edges()
        self.assertEqual(len(edges), 1)

        e1.delete()
        v2.delete()

    def test_relationship_control(self):
        """ Test Relationship Constraint system """

        # setup relationship
        relationship = self.relationship_base_cls(self.edge_model, self.vertex_model)
        self.assertTrue(relationship.allowed(self.edge_model, self.vertex_model))

        class BadEdgeModel(object):
            pass

        class BadVertexModel(object):
            pass

        self.assertFalse(relationship.allowed(self.edge_model, BadVertexModel))
        self.assertFalse(relationship.allowed(BadEdgeModel, self.vertex_model))
        self.assertFalse(relationship.allowed(BadEdgeModel, BadVertexModel))

    def test_relationship_query(self):
        """ Test Relationship Query system

        The Query tests are in a separate tests, we only care that we get the same instantiated query class and
        functionally operates
        """

        # setup relationship
        relationship = self.relationship_base_cls(self.edge_model, self.vertex_model)
        relationship.top_level_vertex = self.vertex_start
        relationship.top_level_vertex_class = self.vertex_model

        v2 = self.vertex_model.create(name='other side relationship')
        e1 = self.edge_model.create(v2, self.vertex_start)

        from mogwai.models import Query, IN

        # default query
        query = relationship.query()
        self.assertIsInstance(query, Query)
        result = query.direction(IN)._get_partial()
        self.assertEqual(result, "g.v(id).query().labels('test_edge_model').direction(IN)")

        # specified edge_types query
        query = relationship.query(edge_types=self.edge_model)
        self.assertIsInstance(query, Query)
        result = query.direction(IN)._get_partial()
        self.assertEqual(result, "g.v(id).query().labels('test_edge_model').direction(IN)")

        e1.delete()
        v2.delete()

    def test_relationship_creation(self):
        """ Test Relationship Vertex and Edge Creation mechanism """

        # setup relationship
        relationship = self.relationship_base_cls(TestEdge2Model, TestVertex2Model)
        relationship.top_level_vertex = self.vertex_start
        relationship.top_level_vertex_class = self.vertex_model

        e1, v2 = relationship.create(edge_params={}, vertex_params={'name': 'other side relationship'})
        self.assertIsInstance(e1, Edge)
        self.assertIsInstance(v2, Vertex)

        vertex_result = relationship.vertices()
        self.assertEqual(len(vertex_result), 1)
        self.assertEqual(vertex_result[0], v2)

        edge_result = relationship.edges()
        self.assertEqual(len(edge_result), 1)
        self.assertEqual(edge_result[0], e1)

        e1.delete()
        v2.delete()