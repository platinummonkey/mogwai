from __future__ import unicode_literals, print_function

import sys
import datetime
from pytz import timezone, utc
from mogwai.connection import execute_query
from mogwai.constants import Configuration
from mogwai.gremlin import GremlinMethod
from mogwai.properties import String, Text
from mogwai.models import Vertex, Edge
from mogwai.exceptions import MogwaiMigrationException
from models import MigrationRoot, Migration, PerformedMigration
from state import MigrationCalculation
from utils import get_loaded_models, ask_for_it_by_name
from actions import *


class DatabaseOperation(object):

    def __init__(self, alias, dry_run=False, *args, **kwargs):
        self.alias = alias
        self.dry_run = dry_run
        self.cached_commands = []
        self.cached_indices_to_repair = []
        self.wait_until_registered_index_script = '''
// Block until the SchemaStatus transitions from INSTALLED to REGISTERED
registered = false
before = System.currentTimeMillis()
while (!registered) {
    Thread.sleep(500L)
    mgmt = g.getManagementSystem()
    idx  = mgmt.getGraphIndex("mixedExample")
    registered = true
    for (k in idx.getFieldKeys()) {
        s = idx.getIndexStatus(k)
        registered &= s.equals(SchemaStatus.REGISTERED)
    }
    mgmt.rollback()
}
duration = System.currentTimeMillis() - before
'''
        self.enable_index_script = '''
try {
    mgmt = g.getManagementSystem()
    mgmt.updateIndex({}, SchemaAction.ENABLE_INDEX)
    mgmt.commit()
} catch (err) {
    g.stopTransaction(FAILURE)
    throw(err)
}'''

    def execute(self, script, print_all_errors=True):
        script = '''
try {
    mgmt = g.getManagementSystem();
    {}
    mgmt.commit()
} catch (err) {
    g.stopTransaction(FAILURE)
    throw(err)
}'''.format(script)
        return execute_query(script, {}, True, True)

    def execute_all_cached(self, print_all_errors=True):
        script = "\n".join([s[0] for s in self.cached_commands])
        return self.execute(script, print_all_errors=print_all_errors)

    def run_repair(self, index_key, edge_key=""):
        c = Configuration()
        backend_database = c.backend_database
        properties_file = c.database_properties_file
        if edge_key is None:
            edge_key = ""

        algorithm = ""
        if backend_database == c.BackendDatabases.CASSANDRA:
            algorithm = ', "org.apache.cassandra.dht.Murmur3Partitioner"'

        script = '''
try {
    TitanIndexRepair.{}Repair(properties_file, index_key, edge_key{})
} catch (err) {
    g.stopTransaction(FAILURE)
    throw(err)
}'''.format(backend_database, algorithm)

        return execute_query(script,
                             {'index_key': index_key, 'edge_key': edge_key, 'properties_file': properties_file},
                             True,
                             True)

    def run_all_cached_index_repairs(self):
        results = []
        for index_key, edge_key in self.cached_indices_to_repair:
            results.append(self.run_repair(index_key, edge_key))
        return results

    def _command(self, cache, cmd, index_key, edge_key):
        if cache:
            self.cached_commands.append(cmd)
            self.cached_indices_to_repair.append((index_key, edge_key))
        else:
            pass

    # Create
    def create_vertex_type(self, state, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")

    def create_edge_type(self, state, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")

    def send_create_signal(self, etype, name, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")

    def create_property_key(self, state, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")

    def create_composite_index(self, state, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")

    # Delete
    def delete_vertex_type(self, state, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")

    def delete_edge_type(self, state, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")

    def send_delete_signal(self, etype, name, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")

    def delete_property_key(self, state, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")

    def delete_composite_index(self, state, cache=False, *args, **kwargs):
        cmd = ""
        self._command(cache, cmd, "", "")
