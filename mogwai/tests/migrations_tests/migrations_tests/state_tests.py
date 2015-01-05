from __future__ import unicode_literals
import copy

from nose.plugins.attrib import attr

from mogwai.tests.base import BaseMogwaiTestCase, TestVertexModel, TestEdgeModel
from mogwai.migrations.migrations.state import MockVertex, MockEdge, MigrationCalculation, MigrationChanges


@attr('unit', 'migration_tests', 'migration_tests_state')
class TestMigrationStateCalculation(BaseMogwaiTestCase):
    """ Test the state module in migrations """

    def test_property_addition_state_calculation_vertex(self):
        previous_vertex = MockVertex(TestVertexModel.element_type, {})
        current_vertex = TestVertexModel
        migration = MigrationCalculation.property_migrations(previous_vertex, current_vertex)
        self.assertIsInstance(migration, MigrationChanges)
        self.assertIsInstance(migration.additions, dict)
        self.assertEqual(len(TestVertexModel._properties), len(migration.additions))
        self.assertDictEqual({}, migration.deletions)
        self.assertDictEqual({}, migration.changes)

        self.assertDictEqual(migration.current, TestVertexModel._properties)
        self.assertEqual(migration.model, TestVertexModel)

    def test_property_addition_state_calculation_edge(self):
        previous_edge = MockEdge(TestEdgeModel.label, {})
        current_edge = TestEdgeModel
        migration = MigrationCalculation.property_migrations(previous_edge, current_edge)
        self.assertIsInstance(migration, MigrationChanges)
        self.assertIsInstance(migration.additions, dict)
        self.assertEqual(len(TestEdgeModel._properties), len(migration.additions))
        self.assertDictEqual({}, migration.deletions)
        self.assertDictEqual({}, migration.changes)

        self.assertDictEqual(migration.current, TestEdgeModel._properties)
        self.assertEqual(migration.model, TestEdgeModel)

    def test_property_deletion_state_calculation_vertex(self):
        current_vertex = MockVertex(TestVertexModel.element_type, {})
        previous_vertex = TestVertexModel
        migration = MigrationCalculation.property_migrations(previous_vertex, current_vertex)
        self.assertIsInstance(migration, MigrationChanges)
        self.assertIsInstance(migration.deletions, dict)
        self.assertEqual(len(TestVertexModel._properties), len(migration.deletions))
        self.assertDictEqual({}, migration.additions)
        self.assertDictEqual({}, migration.changes)

        self.assertDictEqual(migration.current, current_vertex._properties)
        self.assertEqual(migration.model, current_vertex)

    def test_property_deletion_state_calculation_edge(self):
        current_edge = MockEdge(TestEdgeModel.label, {})
        previous_edge = TestEdgeModel
        migration = MigrationCalculation.property_migrations(previous_edge, current_edge)
        self.assertIsInstance(migration, MigrationChanges)
        self.assertIsInstance(migration.deletions, dict)
        self.assertEqual(len(TestEdgeModel._properties), len(migration.deletions))
        self.assertDictEqual({}, migration.additions)
        self.assertDictEqual({}, migration.changes)

        self.assertDictEqual(migration.current, current_edge._properties)
        self.assertEqual(migration.model, current_edge)

    def test_property_changes_state_calculation_vertex(self):
        current_vertex = MockVertex(TestVertexModel.element_type, copy.deepcopy(TestVertexModel._properties))
        name_prop = copy.copy(current_vertex._properties.get('name'))
        name_prop.required = not name_prop.required
        current_vertex._properties['name'] = name_prop
        previous_vertex = TestVertexModel

        migration = MigrationCalculation.property_migrations(previous_vertex, current_vertex)
        self.assertIsInstance(migration, MigrationChanges)
        self.assertDictEqual({}, migration.additions)
        self.assertDictEqual({}, migration.deletions)

        self.assertIsInstance(migration.changes, dict)
        self.assertEqual(1, len(migration.changes))
        self.assertIsInstance(migration.changes.values()[0], (list, tuple))
        self.assertIsInstance(migration.changes.values()[0][0], MigrationChanges)
        self.assertEqual(name_prop._definition(), migration.changes.values()[0][0].current._definition())

        self.assertDictEqual(migration.current, current_vertex._properties)
        self.assertEqual(migration.model, current_vertex)

    def test_property_changes_state_calculation_edge(self):
        current_edge = MockEdge(TestEdgeModel.label, copy.deepcopy(TestEdgeModel._properties))
        name_prop = copy.copy(current_edge._properties.get('name'))
        name_prop.required = not name_prop.required
        current_edge._properties['name'] = name_prop
        previous_edge = TestEdgeModel

        migration = MigrationCalculation.property_migrations(previous_edge, current_edge)
        self.assertIsInstance(migration, MigrationChanges)
        self.assertDictEqual({}, migration.additions)
        self.assertDictEqual({}, migration.deletions)

        self.assertIsInstance(migration.changes, dict)
        self.assertEqual(1, len(migration.changes))
        self.assertIsInstance(migration.changes.values()[0], (list, tuple))
        self.assertIsInstance(migration.changes.values()[0][0], MigrationChanges)
        self.assertEqual(name_prop._definition(), migration.changes.values()[0][0].current._definition())

        self.assertDictEqual(migration.current, current_edge._properties)
        self.assertEqual(migration.model, current_edge)