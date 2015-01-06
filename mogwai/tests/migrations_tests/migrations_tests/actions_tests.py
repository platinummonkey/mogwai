from __future__ import unicode_literals

from nose.plugins.attrib import attr

from mogwai.tests.base import BaseMogwaiTestCase
from mogwai.migrations.migrations.actions import *
from mogwai.tests.base import TestVertexModel, TestEdgeModel
from mogwai.exceptions import MogwaiMigrationException
from mogwai.index.index import CompositeIndex


@attr('unit', 'migration_tests', 'migration_tests_action')
class TestMigrationActions(BaseMogwaiTestCase):
    """ Test the actions module in migrations """

    def test_base_action_get_model_info(self):
        mv = MockVertex('test_vertex', {}, {}, 'TestVertex')
        me = MockEdge('test_edge', {}, {}, 'TestEdge')

        r = Action.get_model_info(TestVertexModel)
        self.assertIsInstance(r, tuple)
        self.assertEqual(3, len(r))
        self.assertListEqual(['vertex', 'mogwai.tests.base.TestVertexModel', 'test_vertex_model'], list(r))

        r = Action.get_model_info(TestEdgeModel)
        self.assertIsInstance(r, tuple)
        self.assertEqual(3, len(r))
        self.assertListEqual(['edge', 'mogwai.tests.base.TestEdgeModel', 'test_edge_model'], list(r))

        r = Action.get_model_info(mv)
        self.assertIsInstance(r, tuple)
        self.assertEqual(3, len(r))
        self.assertListEqual(['vertex', 'TestVertex', 'test_vertex'], list(r))

        r = Action.get_model_info(me)
        self.assertIsInstance(r, tuple)
        self.assertEqual(3, len(r))
        self.assertListEqual(['edge', 'TestEdge', 'test_edge'], list(r))

        with self.assertRaises(MogwaiMigrationException):

            class Test(object):
                pass

            Action.get_model_info(Test)

        with self.assertRaises(MogwaiMigrationException):
            Action.get_model_info(None)

    def test_add_element_type_action(self):
        action = AddElementType(TestVertexModel, 'test')
        self.assertEqual(" + Added element type 'mogwai.tests.base.TestVertexModel' for package 'test'",
                         action.console_line())

        self.assertEqual("""        # Adding vertex 'mogwai.tests.base.TestVertexModel'
        db.create_vertex_type('test_vertex_model')\n""", action.forwards_code())
        self.assertEqual("""        # Deleting vertex 'mogwai.tests.base.TestVertexModel'
        db.delete_vertex_type('test_vertex_model')\n""", action.backwards_code())

        forwards_actions = []
        backwards_actions = []
        action.add_forwards(forwards_actions)
        action.add_backwards(backwards_actions)

        self.assertEqual(1, len(forwards_actions))
        self.assertEqual(1, len(backwards_actions))

        self.assertEqual("""        # Adding vertex 'mogwai.tests.base.TestVertexModel'
        db.create_vertex_type('test_vertex_model')\n""", forwards_actions[0])
        self.assertEqual("""        # Deleting vertex 'mogwai.tests.base.TestVertexModel'
        db.delete_vertex_type('test_vertex_model')\n""", backwards_actions[0])

    def test_delete_element_type_action(self):
        action = DeleteElementType(TestVertexModel, 'test')
        self.assertEqual(" - Deleted element type 'mogwai.tests.base.TestVertexModel' for package 'test'",
                         action.console_line())

        self.assertEqual("""        # Deleting vertex 'mogwai.tests.base.TestVertexModel'
        db.delete_vertex_type('test_vertex_model')\n""", action.forwards_code())
        self.assertEqual("""        # Adding vertex 'mogwai.tests.base.TestVertexModel'
        db.create_vertex_type('test_vertex_model')\n""", action.backwards_code())

        forwards_actions = []
        backwards_actions = []
        action.add_forwards(forwards_actions)
        action.add_backwards(backwards_actions)

        self.assertEqual(1, len(forwards_actions))
        self.assertEqual(1, len(backwards_actions))

        self.assertEqual("""        # Deleting vertex 'mogwai.tests.base.TestVertexModel'
        db.delete_vertex_type('test_vertex_model')\n""", forwards_actions[0])
        self.assertEqual("""        # Adding vertex 'mogwai.tests.base.TestVertexModel'
        db.create_vertex_type('test_vertex_model')\n""", backwards_actions[0])

    def test_add_property_action(self):
        prop = TestVertexModel._properties['name']
        action = AddProperty(TestVertexModel, prop, package_name='test')
        self.assertEqual(" + Added element property 'name' to 'mogwai.tests.base.TestVertexModel' for package 'test'",
                         action.console_line())

        self.assertEqual("""        # Adding element property 'mogwai.tests.base.TestVertexModel.name'
        db.create_property_key("testvertexmodel_name", data_type="String")\n""", action.forwards_code())
        self.assertEqual("""        # Deleting element property 'mogwai.tests.base.TestVertexModel.name'
        db.delete_property_key("testvertexmodel_name")\n""", action.backwards_code())

        forwards_actions = []
        backwards_actions = []
        action.add_forwards(forwards_actions)
        action.add_backwards(backwards_actions)

        self.assertEqual(1, len(forwards_actions))
        self.assertEqual(1, len(backwards_actions))

        self.assertEqual("""        # Adding element property 'mogwai.tests.base.TestVertexModel.name'
        db.create_property_key("testvertexmodel_name", data_type="String")\n""", forwards_actions[0])
        self.assertEqual("""        # Deleting element property 'mogwai.tests.base.TestVertexModel.name'
        db.delete_property_key("testvertexmodel_name")\n""", backwards_actions[0])

    def test_delete_property_action(self):
        prop = TestVertexModel._properties['name']
        action = DeleteProperty(TestVertexModel, prop, package_name='test')
        self.assertEqual(" - Deleted element property 'name' to 'mogwai.tests.base.TestVertexModel' for package 'test'",
                         action.console_line())

        self.assertEqual("""        # Deleting element property 'mogwai.tests.base.TestVertexModel.name'
        db.delete_property_key("testvertexmodel_name")\n""", action.forwards_code())
        self.assertEqual("""        # Adding element property 'mogwai.tests.base.TestVertexModel.name'
        db.create_property_key("testvertexmodel_name", data_type="String")\n""", action.backwards_code())

        forwards_actions = []
        backwards_actions = []
        action.add_forwards(forwards_actions)
        action.add_backwards(backwards_actions)

        self.assertEqual(1, len(forwards_actions))
        self.assertEqual(1, len(backwards_actions))

        self.assertEqual("""        # Deleting element property 'mogwai.tests.base.TestVertexModel.name'
        db.delete_property_key("testvertexmodel_name")\n""", forwards_actions[0])
        self.assertEqual("""        # Adding element property 'mogwai.tests.base.TestVertexModel.name'
        db.create_property_key("testvertexmodel_name", data_type="String")\n""", backwards_actions[0])

    def test_add_composite_index_action(self):
        pass

    def test_delete_composite_index_action(self):
        pass
