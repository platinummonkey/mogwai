from __future__ import unicode_literals
from nose.plugins.attrib import attr
from mogwai.models import Vertex, Edge
from mogwai.properties import String, Integer
from mogwai.exceptions import MogwaiRelationshipException
from mogwai.tests.base import BaseMogwaiTestCase, TestVertexModel, counter
from mogwai.relationships.base import Relationship


class TestRelationshipEdgeModel(Edge):
    label = 'test_relationship_edge_model'

    name = String(default='test_edge')
    test_val = Integer(default=counter)


class TestRelationshipVertexModel(Vertex):
    element_type = 'test_relationship_vertex_model'

    name = String(default='test_vertex')
    test_val = Integer(default=counter)

    relation = Relationship(TestRelationshipEdgeModel, TestVertexModel)


@attr('unit', 'relationship')
class GraphRelationshipVertexIOTestCase(BaseMogwaiTestCase):
    """ Test Relationship Vertex IO Functionality """

    @classmethod
    def setUpClass(cls):
        super(GraphRelationshipVertexIOTestCase, cls).setUpClass()
        cls.relationship_base_cls = Relationship
        cls.edge_model = TestRelationshipEdgeModel
        cls.vertex_model = TestRelationshipVertexModel

    def test_instantiation(self):
        """ Test that the Relationship is properly Instantiated """

        v1 = self.vertex_model.create(name='test relationship')
        # setup relationship
        self.assertIsNotNone(v1.relation.top_level_vertex_class)
        self.assertIsNotNone(v1.relation.top_level_vertex)
        self.assertEqual(v1.relation.top_level_vertex, v1)
        v1.delete()

    def test_follow_through(self):
        """ Test that the Relationship property functions """

        v1 = self.vertex_model.create(name='test relationship')
        e1, v2 = v1.relation.create(vertex_params={'name': 'new relation'})

        e1q = v1.outE(TestRelationshipEdgeModel)[0]
        v2q = v1.outV(TestRelationshipEdgeModel)[0]

        self.assertEqual(e1, e1q)
        self.assertEqual(v2, v2q)

        e1.delete()
        v1.delete()
        v2.delete()