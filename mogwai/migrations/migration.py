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


def _str(value):
        """ Formats a value with escaped strings """
        return '\"{}\"'.format(value)


class DatabaseOperation(object):

    make = ".make()"

    _get_management_system = "mgmt = g.getManagementSystem()"
    _commit_management_system = "mgmt.commit()"
    _rollback_management_system = "mgmt.rollback()"

    _get_property_key = "mgmt.getPropertyKey({key})"
    _get_relation_type = "mgmt.getRelationType({key})"
    _get_relation_types = "mgmt.getRelationTypes({element_label_type}.class)"
    _get_relation_index = "mgmt.getRelationIndex({key}, {edge_key})"
    _get_graph_index = "mgmt.getGraphIndex({key})"
    _contains_relation_type = "mgmt.containsRelationType({key})"

    _make_vertex_label = "mgmt.makeVertexLabel({key})"
    _make_edge_label = "mgmt.makeEdgeLabel({key})"
    _make_property_key = "mgmt.makePropertyKey({key})"
    _change_index_name = "mgmt.changeName({index}, {key})"

    _set_static = ".setStatic()"
    _set_ttl = ".setTTL({variable}, {time}, {time_unit})"
    _set_cardinality = ".cardinality({cardinality})"
    _set_dataType = ".dataType({data_type}.class)"
    _set_multiplicity = ".multiplicity({multiplicity})"
    _set_unidirected = ".unidirected()"

    # Schema Actions
    _register_index = "SchemaAction.REGISTER_INDEX"
    _enable_index = "SchemaAction.ENABLE_INDEX"
    _update_index = "mgmt.updateIndex({index}, {schema_action})"
    _get_index_status = ".getIndexStatus({index})"

    _wait_until_registered_index_script = '''
// Block until the SchemaStatus transitions from INSTALLED to REGISTERED
registered = false
before = System.currentTimeMillis()
while (!registered) {
    Thread.sleep(500L)
    mgmt2 = g.getManagementSystem()
    idx  = mgmt2.getGraphIndex({key})
    registered = true
    for (k in idx.getFieldKeys()) {
        s = idx.getIndexStatus(k)
        registered &= s.equals(SchemaStatus.REGISTERED)
    }
    mgmt2.rollback()
}
duration = System.currentTimeMillis() - before
'''

    # job index repair
    _index_repair = "TitanIndexRepair.{}Repair({}, {}, {}{})"
    _default_cassandra_partitioner = '"org.apache.cassandra.dht.Murmur3Partitioner"'
    _default_hbase_partitioner = ""

    class TimeUnit(object):
        MILLISECONDS = "TimeUnit.MILLISECONDS"
        SECONDS = "TimeUnit.SECONDS"
        MINUTES = "TimeUnit.MINUTES"
        HOURS = "TimeUnit.HOURS"
        DAYS = "TimeUnit.DAYS"

    class Cardinality(object):
        SINGLE = "Cardinality.SINGLE"
        LIST = "Cardinality.LIST"
        SET = "Cardinality.SET"

    class DataTypes(object):
        OBJECT = "Object"
        STRING = "String"
        CHARACTER = "Character"
        BOOLEAN = "Boolean"
        BYTE = "Byte"
        SHORT = "Short"
        INTEGER = "Integer"
        LONG = "Long"
        FLOAT = "Float"
        DOUBLE = "Double"
        DECIMAL = "Decimal"
        PRECISION = "Precision"
        GEOSHAPE = "GeoShape"

    class Multiplicity(object):
        MULTI = "Multiplicity.MULTI"
        SIMPLE = "Multiplicity.SIMPLE"
        MANY2ONE = "Multiplicity.MANY2ONE"
        ONE2MANY = "Multiplicity.ONE2MANY"
        ONE2ONE = "Multiplicity.ONE2ONE"

    def __init__(self, alias, dry_run=False, *args, **kwargs):
        self.alias = alias
        self.dry_run = dry_run
        self.cached_commands = []
        self.cached_indices_to_repair = []

        self.partitioner = ""
        if 'partitioner' in kwargs:
            self.partitioner = kwargs.get("partitioner", "")

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

    def _command(self, cmd, index_key, edge_key):
        self.cached_commands.append(cmd)
        self.cached_indices_to_repair.append((index_key, edge_key))

    # Create
    def create_vertex_type(self, state, **kwargs):
        cmd = ""
        self._command(cmd, "", "")

    def create_edge_type(self, edge_label, **kwargs):
        cmd = "{label}{}{unidirected}{make}"
        self._make_edge_label.format(_str(edge_label))
        self._command(cmd, "", "")

    def send_create_signal(self, etype, name, **kwargs):
        cmd = ""
        self._command(cmd, "", "")

    def create_property_key(self, state, **kwargs):
        cmd = ""
        self._command(cmd, "", "")

    def create_composite_index(self, state, **kwargs):
        cmd = ""
        self._command(cmd, "", "")

    # Delete
    def delete_vertex_type(self, state, **kwargs):
        cmd = ""
        self._command(cmd, "", "")

    def delete_edge_type(self, state, **kwargs):
        cmd = ""
        self._command(cmd, "", "")

    def send_delete_signal(self, etype, name, **kwargs):
        cmd = ""
        self._command(cmd, "", "")

    def delete_property_key(self, state, **kwargs):
        cmd = ""
        self._command(cmd, "", "")

    def delete_composite_index(self, state, **kwargs):
        cmd = ""
        self._command(cmd, "", "")
