from __future__ import unicode_literals
from mogwai._compat import string_types, array_types
import logging
from re import compile
from rexpro.utils import get_rexpro
from rexpro.exceptions import RexProConnectionException, RexProScriptException

from mogwai.exceptions import MogwaiConnectionError, MogwaiQueryError
from mogwai.metrics.manager import MetricManager
from mogwai.constants import Configuration as __Configuration

logger = logging.getLogger(__name__)


SOCKET_TYPE = None
CONNECTION_TYPE = None
CONNECTION_POOL_TYPE = None
_connection_pool = None
metric_manager = MetricManager()
__cached_spec = None
Configuration = __Configuration()


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
            _connection_pool.close_connection(conn, soft=True)
            raise MogwaiConnectionError("Connection Error during query - {}".format(ce))
        except RexProScriptException as se:  # pragma: no cover
            _connection_pool.close_connection(conn, soft=True)
            raise MogwaiQueryError("Error during query - {}".format(se))
        except:  # pragma: no cover
            _connection_pool.close_connection(conn, soft=True)
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
        raise MogwaiConnectionError("Must Specify at least one host or list of hosts: host: {}, graph_name: {}".format(
            host, graph_name)
        )
