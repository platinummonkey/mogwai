from __future__ import unicode_literals
from _compat import string_types, array_types
import logging
from re import compile
from random import shuffle
from rexpro.connection import RexProConnection
from rexpro.exceptions import RexProConnectionException, RexProScriptException

from mogwai.exceptions import MogwaiConnectionError, MogwaiQueryError
from mogwai.metrics.manager import MetricManager
from mogwai._compat import print_

logger = logging.getLogger(__name__)


_connections = []
_graph_name = None
metric_manager = MetricManager()
_loaded_models = []
__cached_spec = None


@metric_manager.time_calls
def execute_query(query, params={}, transaction=True, isolate=True, *args, **kwargs):
    """
    Execute a raw Gremlin query with the given parameters passed in.

    :param query: The Gremlin query to be executed
    :type query: str
    :param params: Parameters to the Gremlin query
    :type params: dict
    :param context: String context data to include with the query for stats logging
    :rtype: dict

    """
    if len(_connections) <= 0:  # pragma: no cover
        raise MogwaiConnectionError('Must call mogwai.connection.setup before querying.')

    conn = _connections[0]
    """ @type conn: rexpro.RexProConnection """
    try:
        response = conn.execute(query, params=params, isolate=isolate, transaction=transaction)
        print_("Got raw response: %s" % response)

    except RexProConnectionException as ce:  # pragma: no cover
        raise MogwaiConnectionError("Connection Error during query - {}".format(ce))
    except RexProScriptException as se:  # pragma: no cover
        raise MogwaiQueryError("Error during query - {}".format(se))
    except:  # pragma: no cover
        raise

    logger.debug(response)

    return response


_host_re = compile(r'^((?P<user>.+?)(:(?P<password>.*?))?@)?(?P<host>.*?)(:(?P<port>\d+?))?(?P<graph_name>/.*?)?$')


def _parse_host(host, username, password, graph_name):
        m = _host_re.match(host)
        d = m.groupdict() if m is not None else {}
        host = d.get('host', None) or '127.0.0.1'
        port = int(d.get('port', None) or 8184)
        username = d.get('username', None) or username
        password = d.get('password', None) or password
        graph_name = d.get('graph_name', None) or graph_name
        return {'host': host, 'port': port, 'username': username, 'password': password, 'graph_name': graph_name}


def setup(hosts, graph_name='graph', username='', password='', metric_reporters=None):
    """  Sets up the connection, and instantiates the models

    """
    global _connections
    global metric_manager

    if metric_reporters:  # pragma: no cover
        metric_manager.setup_reporters(metric_reporters)

    if isinstance(hosts, string_types):
        _connections.append(RexProConnection(**_parse_host(hosts, username, password, graph_name)))
    elif isinstance(hosts, array_types):  # pragma: no cover
        for host in hosts:
            _connections.append(RexProConnection(**_parse_host(host, username, password, graph_name)))

        shuffle(_connections)
    else:  # pragma: no cover
        raise MogwaiConnectionError("Must Specify at least one host or list of hosts")


def _add_model_to_space(model):
    global _loaded_models
    _loaded_models.append(model)


def generate_spec():
    """ Generates a titan index and type specification document based on loaded Vertex and Edge models """
    global _loaded_models, __cached_spec
    if __cached_spec:
        return __cached_spec
    from mogwai.models import Edge
    spec_list = []
    for model in _loaded_models:
        if not model.__abstract__ and hasattr(model, 'get_element_type'):

            makeType = 'makeLabel' if issubclass(model, Edge) else 'makeKey'
            element_type = 'Edge' if issubclass(model, Edge) else 'Vertex'

            spec = {'model': model.get_element_type(),
                    'element_type': element_type,
                    'makeType': makeType,
                    'properties': {}}
            for property in model._properties.values():
                if property.index:
                    # Only set this up for indexed properties

                    # Uniqueness constraint
                    uniqueness = ""
                    if property.unique and property.unique.lower() == 'in':
                        uniqueness = ".unique()"
                    elif property.unique and property.unique.lower() == 'out':
                        uniqueness = ".unidirected()"
                    elif property.unique and property.unique.lower() == 'both':
                        uniqueness = ".unique().single()"
                    if property.unique and property.unique.lower() == 'list':
                        uniqueness += ".list()"

                    # indexing extensions support
                    if not property.index_ext:
                        index_ext = ""
                    else:
                        index_ext = ".indexed(%s)" % property.index_ext

                    #compiled_index = {"script": "g.createKeyIndex(name, {}.class).dataType({}.class){}{}.make(); g.commit()".format(
                    #    element_type,
                    #    property.data_type,
                    #    index_ext,
                    #    uniqueness),
                    compiled_index = {"script": "g.{}(name).dataType({}.class).indexed({}{}.class){}.make(); g.commit()".format(
                        makeType,
                        property.data_type,
                        index_ext,
                        element_type,
                        uniqueness),
                                      "params": {'name': property.db_field_name},
                                      "transaction": False}
                    spec['properties'][property.db_field_name] = {
                        'data_type': property.data_type,
                        'index_ext': index_ext,
                        'uniqueness': uniqueness,
                        'compiled': compiled_index,
                    }

            spec_list.append(spec)
    __cached_spec = spec_list
    return spec_list


def sync_spec(filename, host, graph_name='graph', username='', password='', dry_run=False):  # pragma: no cover
    """
    Sync the given spec file to mogwai.

    @param filename: The filename of the spec file
        @type filename: str
    @param host: The host the be synced
        @type host: str
    @param graph_name: The name of the graph to be synced
        @type graph_name: str
    @param dry_run: Only prints generated Gremlin if True
        @type dry_run: boolean
    @returns: None

    """
    conn = RexProConnection(graph_name=graph_name, **_parse_host(host, username, password, graph_name))
    #Spec(filename).sync(conn, dry_run=dry_run)
    pass
