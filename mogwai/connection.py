from __future__ import unicode_literals
from mogwai._compat import string_types, array_types
import logging
from re import compile
from rexpro.connection import RexProConnection
from rexpro.utils import get_rexpro
from rexpro.exceptions import RexProConnectionException, RexProScriptException

from mogwai.exceptions import MogwaiConnectionError, MogwaiQueryError
from mogwai.metrics.manager import MetricManager

logger = logging.getLogger(__name__)


SOCKET_TYPE = None
CONNECTION_TYPE = None
CONNECTION_POOL_TYPE = None
_connection_pool = None
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
    global _connection_pool
    """ :type _connection_pool: RexProConnectionPool | None """

    if not _connection_pool:  # pragma: no cover
        raise MogwaiConnectionError('Must call mogwai.connection.setup before querying.')

    with _connection_pool.connection() as conn:
        try:
            response = conn.execute(query, params=params, isolate=isolate, transaction=transaction)

        except RexProConnectionException as ce:  # pragma: no cover
            raise MogwaiConnectionError("Connection Error during query - {}".format(ce))
        except RexProScriptException as se:  # pragma: no cover
            raise MogwaiQueryError("Error during query - {}".format(se))
        except:  # pragma: no cover
            raise

        logger.debug(response)
        return response


_host_re = compile(r'^((?P<user>.+?)(:(?P<password>.*?))?@)?(?P<host>.*?)(:(?P<port>\d+?))?(?P<graph_name>/.*?)?$')


def _parse_host(host, username, password, graph_name, graph_obj_name='g'):
        m = _host_re.match(host)
        d = m.groupdict() if m is not None else {}
        host = d.get('host', None) or '127.0.0.1'
        port = int(d.get('port', None) or 8184)
        username = d.get('username', None) or username
        password = d.get('password', None) or password
        graph_name = d.get('graph_name', None) or graph_name
        graph_obj_name = graph_obj_name or 'g'
        return {'host': host, 'port': port,
                'username': username, 'password': password,
                'graph_name': graph_name, 'graph_obj_name': graph_obj_name}


def setup(host, graph_name='graph', graph_obj_name='g', username='', password='',
          metric_reporters=None, pool_size=10, concurrency='sync'):
    """  Sets up the connection, and instantiates the models

    """
    global _connection_pool
    global SOCKET_TYPE, CONNECTION_TYPE, CONNECTION_POOL_TYPE
    global metric_manager

    if metric_reporters:  # pragma: no cover
        metric_manager.setup_reporters(metric_reporters)

    sock, conn, pool = get_rexpro(stype=concurrency)
    # store for reference
    SOCKET_TYPE = sock
    CONNECTION_TYPE = conn
    CONNECTION_POOL_TYPE = pool

    if isinstance(host, string_types):
        _connection_pool = pool(pool_size=pool_size,
                                **_parse_host(host, username, password, graph_name, graph_obj_name))

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


def sync_spec(filename, host, graph_name='graph', graph_obj_name='g', username='', password='', dry_run=False):  # pragma: no cover
    """
    Sync the given spec file to mogwai.

    :param filename: The filename of the spec file
    :type filename: str
    :param host: The host the be synced
    :type host: str
    :param graph_name: The name of the graph to be synced
    :type graph_name: str
    :param dry_run: Only prints generated Gremlin if True
    :type dry_run: boolean
    :returns: None

    """
    conn = RexProConnection(graph_name=graph_name, **_parse_host(host, username, password, graph_name, graph_obj_name))
    #Spec(filename).sync(conn, dry_run=dry_run)
    pass
