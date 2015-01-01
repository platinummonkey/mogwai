from __future__ import unicode_literals
from nose.plugins.attrib import attr
from blinker import signal
from functools import partial
from mogwai.tests.base import BaseMogwaiTestCase, TestVertexModel, TestEdgeModel
from mogwai.migrations.operation import DatabaseOperation


@attr('unit', 'migration_tests', 'migration_tests_operation')
class TestMigrationDatabaseOperations(BaseMogwaiTestCase):
    """ Test the state module in migrations """

    db = None

    def setUp(self):
        self.db = DatabaseOperation("testmodel", dry_run=True)

    def test_create_vertex_type(self):
        self.db.create_vertex_type('myvertex', set_ttl=True, ttl_time_value=1,
                                   ttl_time_unit=DatabaseOperation.TimeUnit.HOURS)
        self.assertEqual(2, len(self.db.cached_commands))
        self.assertEqual('testmodel_myvertex = mgmt.makeVertexLabel("myvertex").make()', self.db.cached_commands[0])
        self.assertEqual('mgmt.setTTL(testmodel_myvertex, 1, TimeUnit.HOURS).make()', self.db.cached_commands[1])
        self.assertEqual(('testmodel_myvertex', ('testmodel', 'myvertex', '')), self.db.cached_vars.items()[0])
        self.assertEqual('try {\n'
                         '    mgmt = g.getManagementSystem();\n\n'
                         '    testmodel_myvertex = mgmt.makeVertexLabel("myvertex").make()\n'
                         '    mgmt.setTTL(testmodel_myvertex, 1, TimeUnit.HOURS).make()\n'
                         '\n    mgmt.commit()\n\n'
                         '} catch (err) {\n'
                         '    mgmt.rollback()\n'
                         '    g.stopTransaction(FAILURE)\n'
                         '    throw(err)\n'
                         '}\n', self.db._generate_script())

    def test_create_edge_type(self):
        self.db.create_edge_type('myedge', set_ttl=True, ttl_time_value=1,
                                 ttl_time_unit=DatabaseOperation.TimeUnit.HOURS)
        self.assertEqual(2, len(self.db.cached_commands))
        self.assertEqual('testmodel_myedge = mgmt.makeEdgeLabel("myedge").multiplicity(Multiplicity.MULTI).make()',
                         self.db.cached_commands[0])
        self.assertEqual('mgmt.setTTL(testmodel_myedge, 1, TimeUnit.HOURS).make()', self.db.cached_commands[1])
        self.assertEqual(('testmodel_myedge', ('testmodel', 'myedge', '')), self.db.cached_vars.items()[0])
        self.assertEqual('try {\n'
                         '    mgmt = g.getManagementSystem();\n\n'
                         '    testmodel_myedge = mgmt.makeEdgeLabel("myedge").multiplicity(Multiplicity.MULTI).make()\n'
                         '    mgmt.setTTL(testmodel_myedge, 1, TimeUnit.HOURS).make()\n'
                         '\n    mgmt.commit()\n\n'
                         '} catch (err) {\n'
                         '    mgmt.rollback()\n'
                         '    g.stopTransaction(FAILURE)\n'
                         '    throw(err)\n'
                         '}\n', self.db._generate_script())

    def test_create_property_key(self):
        self.db.create_property_key("myproperty", data_type="String")
        self.assertEqual(1, len(self.db.cached_commands))
        self.assertEqual('testmodel_myproperty = mgmt.makePropertyKey("myproperty").'
                         'dataType(String.class).cardinality(Cardinality.SINGLE).make()',
                         self.db.cached_commands[0])
        self.assertEqual(('testmodel_myproperty', ('testmodel', 'myproperty', '')),
                         self.db.cached_vars.items()[0])
        self.assertEqual('try {\n'
                         '    mgmt = g.getManagementSystem();\n\n'
                         '    testmodel_myproperty = mgmt.makePropertyKey("myproperty").dataType(String.class).cardinality(Cardinality.SINGLE).make()\n'
                         '\n    mgmt.commit()\n\n'
                         '} catch (err) {\n'
                         '    mgmt.rollback()\n'
                         '    g.stopTransaction(FAILURE)\n'
                         '    throw(err)\n'
                         '}\n', self.db._generate_script())

    def test_create_composite_index(self):
        pass

    def _subscriber(self, catcher, sender, **kwargs):
        catcher.caught_signal = True
        catcher.sender = sender
        catcher.kwargs = kwargs

    def test_send_create_signal(self):
        class SignalCatcher(object):
            caught_signal = False
            sender = None
            kwargs = None

        sc = SignalCatcher()
        sig = signal('mogwai.migration.create_vertex_testsignal')
        sig.connect(partial(self._subscriber, sc), weak=False)

        self.db.send_create_signal('vertex', 'testsignal', mykwarg='test')
        self.assertTrue(sc.caught_signal)
        self.assertDictContainsKey(sc.kwargs, 'mykwarg')

    def test_delete_vertex_type(self):
        self.db.delete_vertex_type("myvertex")
        self.assertEqual('testmodel_myvertex = mgmt.getVertexLabel("myvertex")', self.db.cached_commands[0])
        self.assertEqual('testmodel_myvertex.remove()', self.db.cached_commands[1])
        self.assertEqual(('testmodel_myvertex', ('testmodel', 'myvertex', '')), self.db.cached_vars.items()[0])
        self.assertEqual('try {\n'
                         '    mgmt = g.getManagementSystem();\n\n'
                         '    testmodel_myvertex = mgmt.getVertexLabel("myvertex")\n'
                         '    testmodel_myvertex.remove()\n'
                         '\n    mgmt.commit()\n\n'
                         '} catch (err) {\n'
                         '    mgmt.rollback()\n'
                         '    g.stopTransaction(FAILURE)\n'
                         '    throw(err)\n'
                         '}\n', self.db._generate_script())

    def test_delete_edge_type(self):
        self.db.delete_edge_type("myedge")
        self.assertEqual('testmodel_myedge = mgmt.getEdgeLabel("myedge")', self.db.cached_commands[0])
        self.assertEqual('testmodel_myedge.remove()', self.db.cached_commands[1])
        self.assertEqual(('testmodel_myedge', ('testmodel', 'myedge', '')), self.db.cached_vars.items()[0])
        self.assertEqual('try {\n'
                         '    mgmt = g.getManagementSystem();\n\n'
                         '    testmodel_myedge = mgmt.getEdgeLabel("myedge")\n'
                         '    testmodel_myedge.remove()\n'
                         '\n    mgmt.commit()\n\n'
                         '} catch (err) {\n'
                         '    mgmt.rollback()\n'
                         '    g.stopTransaction(FAILURE)\n'
                         '    throw(err)\n'
                         '}\n', self.db._generate_script())

    def test_delete_property_key(self):
        self.db.delete_property_key("myproperty")
        self.assertEqual('testmodel_myproperty = mgmt.getPropertyKey("myproperty")', self.db.cached_commands[0])
        self.assertEqual('testmodel_myproperty.remove()', self.db.cached_commands[1])
        self.assertEqual(('testmodel_myproperty', ('testmodel', 'myproperty', '')), self.db.cached_vars.items()[0])
        self.assertEqual('try {\n'
                         '    mgmt = g.getManagementSystem();\n\n'
                         '    testmodel_myproperty = mgmt.getPropertyKey("myproperty")\n'
                         '    testmodel_myproperty.remove()\n'
                         '\n    mgmt.commit()\n\n'
                         '} catch (err) {\n'
                         '    mgmt.rollback()\n'
                         '    g.stopTransaction(FAILURE)\n'
                         '    throw(err)\n'
                         '}\n', self.db._generate_script())

    def test_delete_composite_index(self):
        self.db.delete_composite_index("mykey", "myedge")
        self.assertEqual('testmodel_mykey_myedge = mgmt.getGraphIndex("testmodel_mykey_myedge")',
                         self.db.cached_commands[0])
        self.assertEqual('testmodel_mykey_myedge.remove()', self.db.cached_commands[1])
        self.assertEqual(('testmodel_mykey_myedge', ('testmodel', 'mykey', 'myedge')), self.db.cached_vars.items()[0])
        self.assertEqual('try {\n'
                         '    mgmt = g.getManagementSystem();\n\n'
                         '    testmodel_mykey_myedge = mgmt.getGraphIndex("testmodel_mykey_myedge")\n'
                         '    testmodel_mykey_myedge.remove()\n'
                         '\n    mgmt.commit()\n\n'
                         '} catch (err) {\n'
                         '    mgmt.rollback()\n'
                         '    g.stopTransaction(FAILURE)\n'
                         '    throw(err)\n'
                         '}\n', self.db._generate_script())

    def test_send_delete_signal(self):
        class SignalCatcher(object):
            caught_signal = False
            sender = None
            kwargs = None

        sc = SignalCatcher()
        sig = signal('mogwai.migration.delete_vertex_testsignal')
        sig.connect(partial(self._subscriber, sc), weak=False)

        self.db.send_delete_signal('vertex', 'testsignal', mykwarg='test')
        self.assertTrue(sc.caught_signal)
        self.assertDictContainsKey(sc.kwargs, 'mykwarg')
