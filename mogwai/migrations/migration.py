from __future__ import unicode_literals, print_function

import sys
import datetime
from pytz import timezone, utc
from collections import OrderedDict
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

    _var_assignment = "{var} = "
    _make = ".make()"
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
    _build_index = "mgmt.buildIndex({key}, {element_type}.class)"
    _add_key = ".addKey({key})"
    _build_mixed_index = ".buildMixedIndex({key})"
    _set_ttl = "mgmt.setTTL({variable}, {time}, {time_unit})"  # ONLY VALID FOR CASSANDRA

    _set_static = ".setStatic()"
    _set_cardinality = ".cardinality({cardinality})"
    _set_dataType = ".dataType({data_type}.class)"
    _set_multiplicity = ".multiplicity({multiplicity})"
    _set_unidirected = ".unidirected()"
    _set_parition = ".partition()"

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

    def __init__(self, model_name, dry_run=False, *args, **kwargs):
        self.model_name = model_name
        self.dry_run = dry_run
        self.cached_commands = []
        self.cached_vars = OrderedDict()

        self.partitioner = ""
        if 'partitioner' in kwargs:
            self.partitioner = kwargs.get("partitioner", "")

    def _get_or_create_var(self, index_key, edge_key):
        """ Get or create a variable name for the given index

        :param index_key: index key
        :type index_key: basestring
        :param edge_key: edge key
        :type edge_key: basestring
        :return: composite variable name
        """
        composite_key = "{}.{}".format(index_key, edge_key)
        if composite_key not in self.cached_vars:
            self.cached_vars[composite_key] = (self.model_name, index_key, edge_key)
        return composite_key

    def _get_info_for_var(self, var_key):
        if var_key not in self.cached_vars:
            return None
        return self.cached_vars[var_key]

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
        for index_key, cmd_pair in self.cached_commands.items():
            edge_key = cmd_pair[1]
            results.append(self.run_repair(index_key, edge_key))
        return results

    def _command(self, cmd, index_key, edge_key, var_assignment=True):
        if var_assignment:
            cmd = (self._var_assignment + cmd).format(var=self._get_or_create_var(index_key=index_key,
                                                                                  edge_key=edge_key))
        else:
            try:
                # try to assign, variables to existing commands
                cmd = cmd.format(var=self._get_or_create_var(index_key=index_key, edge_key=edge_key))
            except KeyError as e:
                # no variable assignment needed
                pass
        self.cached_commands.append(cmd)

    # Create
    def create_vertex_type(self, vertex_label, **kwargs):
        label = self._make_vertex_label.format(key=_str(vertex_label))
        cmd = "{label}{make}".format(label=label, make=self._make)
        self._command(cmd, vertex_label, "")
        if 'set_ttl' in kwargs:
            self._set_ttl(vertex_label,
                          kwargs.get('ttl_time_value', 1),
                          kwargs.get('ttl_time_unit', DatabaseOperation.TimeUnit.DAYS))

    def create_edge_type(self, edge_label, **kwargs):
        label = self._make_edge_label.format(key=_str(edge_label))
        multiplicty = self._set_multiplicity.format(multiplicity=self.Multiplicity.MULTI)
        unidirected = self._set_unidirected
        cmd = "{label}{multiplicity}{unidirected}{make}".format(label=label, multiplicty=multiplicty,
                                                                unidirected=unidirected, make=self._make)
        self._command(cmd, edge_label, "")
        if 'set_ttl' in kwargs:
            self._set_ttl(edge_label,
                          kwargs.get('ttl_time_value', 1),
                          kwargs.get('ttl_time_unit', DatabaseOperation.TimeUnit.DAYS))

    def create_property_key(self, property_name, data_type=None, cardinality=None, **kwargs):
        if data_type is None:
            data_type = DatabaseOperation.DataTypes.OBJECT
        if cardinality is None:
            cardinality = DatabaseOperation.Cardinality.SINGLE
        prop = self._make_property_key.format(key=property_name)
        datatype = self._set_dataType.format(data_type=data_type)
        cardinality = self._set_cardinality.format(cardinality=cardinality)
        cmd = "{prop}{data_type}{cardinality}".format(
            prop=prop,
            data_type=data_type,
            cardinality=cardinality
        )
        self._command(cmd, property_name, "")

    def create_composite_index(self, index_key, element_type, indexer=None, *args, **kwargs):
        build_index = self._build_index.format(key=index_key, element_type=element_type)
        if indexer is not None:
            indexer = _str(indexer)
        build_mixed_index = self._build_mixed_index.format(key=indexer)
        cmd_set = "".join(args)

        cmd = "{build_index}{cmd_set}{build_mixed_index}".format(
            build_index=build_index,
            cmd_set=cmd_set,
            build_mixed_index=build_mixed_index
        )

        self._command(cmd, index_key, "")

    def send_create_signal(self, etype, name, **kwargs):
        pass

    # Delete
    def delete_vertex_type(self, vertex_label, **kwargs):
        self._command(self._get_graph_index.format(key=vertex_label), vertex_label, "")
        remove_property_cmd = "{var}.remove()"
        self._command(remove_property_cmd, vertex_label, "", var_assignment=False)

    def delete_edge_type(self, edge_label, **kwargs):
        self._command(self._get_relation_type.format(key=edge_label), edge_label, "")
        remove_property_cmd = "{var}.remove()"
        self._command(remove_property_cmd, edge_label, "", var_assignment=False)

    def delete_property_key(self, property_key, **kwargs):
        self._command(self._get_property_key.format(key=property_key), property_key, "")
        remove_property_cmd = "{var}.remove()"
        self._command(remove_property_cmd, property_key, "", var_assignment=False)

    def delete_composite_index(self, index_key, **kwargs):
        self._command(self._get_graph_index.format(key=index_key), index_key, "")
        remove_property_cmd = "{var}.remove()"
        self._command(remove_property_cmd, index_key, "", var_assignment=False)

    def send_delete_signal(self, etype, name, **kwargs):
        pass

    def _set_ttl(self, var_key, time_value, time_unit):
        cmd = "mgmt.setTTL({var}, {time_value}, {time_unit}){make}".format(
            time_value=time_value,
            time_unit=time_unit,
            make=self._make
        )
        self._command(cmd, var_key, "", var_assignment=False)