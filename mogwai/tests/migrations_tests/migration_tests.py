from __future__ import unicode_literals
from nose.plugins.attrib import attr

from mogwai.tests.base import BaseMogwaiTestCase, TestVertexModel, TestEdgeModel
from mogwai.migrations.migration import DatabaseOperation


@attr('unit', 'migration_tests', 'migration_tests_migration')
class TestMigrationDatabaseOperations(BaseMogwaiTestCase):
    """ Test the state module in migrations """

    def test_create_vertex_type(self):
        db = DatabaseOperation("testmodel", dry_run=True)
        db.create_vertex_type('myvertex', set_ttl=True, ttl_time_value=1, ttl_time_unit=db.TimeUnit.HOURS)
        self.assertEqual(2, len(db.cached_commands))
        self.assertEqual('testmodel_myvertex = mgmt.makeVertexLabel("myvertex").make()', db.cached_commands[0])
        self.assertEqual('mgmt.setTTL(testmodel_myvertex, 1, TimeUnit.HOURS).make()', db.cached_commands[1])
        self.assertEqual(('testmodel_myvertex', ('testmodel', 'myvertex', '')), db.cached_vars.items()[0])
        self.assertEqual('try {\n'
                         '    mgmt = g.getManagementSystem();\n\n'
                         '    testmodel_myvertex = mgmt.makeVertexLabel("myvertex").make()\n'
                         '    mgmt.setTTL(testmodel_myvertex, 1, TimeUnit.HOURS).make()\n'
                         '\n    mgmt.commit()\n'
                         '} catch (err) {\n'
                         '    g.stopTransaction(FAILURE)\n'
                         '    throw(err)\n'
                         '}\n', db._generate_script())

    def test_create_edge_type(self):
        db = DatabaseOperation("testmodel", dry_run=True)
        db.create_edge_type('myedge', set_ttl=True, ttl_time_value=1, ttl_time_unit=db.TimeUnit.HOURS)
        self.assertEqual(2, len(db.cached_commands))
        self.assertEqual('testmodel_myedge = mgmt.makeEdgeLabel("myedge").multiplicity(Multiplicity.MULTI).make()', db.cached_commands[0])
        self.assertEqual('mgmt.setTTL(testmodel_myedge, 1, TimeUnit.HOURS).make()', db.cached_commands[1])
        self.assertEqual(('testmodel_myedge', ('testmodel', 'myedge', '')), db.cached_vars.items()[0])
        self.assertEqual('try {\n'
                         '    mgmt = g.getManagementSystem();\n\n'
                         '    testmodel_myedge = mgmt.makeEdgeLabel("myedge").multiplicity(Multiplicity.MULTI).make()\n'
                         '    mgmt.setTTL(testmodel_myedge, 1, TimeUnit.HOURS).make()\n'
                         '\n    mgmt.commit()\n'
                         '} catch (err) {\n'
                         '    g.stopTransaction(FAILURE)\n'
                         '    throw(err)\n'
                         '}\n', db._generate_script())
