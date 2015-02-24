.. _session_wrappers:

Session Management Example
==========================

.. _session_wrappers_sync:
Session Wrapping
----------------

The default connection pool that is used to execute queries uses a new session for every request.
This fully isolates queries from each other, which is a good idea in most cases. There are, however, also
scenarios in which multiple queries need to share some kind of state. This can be done with a special kind of
connection pool, which by default spawns connections that use the same session.

.. literalinclude:: code/session_wrappers_sync.py
    :language: python
    :linenos:

.. _session_wrappers_conc:
Concurrent Session Wrapping
---------------------------

.. note:: The pool needs to be referenced explicitly by querying methods in the wrapper when the connection to Rexster
            is set up with e.g. `eventlet` or `gevent`.

The type of concurrency that is available in mogwai and rexpro is based on coroutines,
which share the same global context. It would thus be unsafe to keep the session or its associated pool in a global
variable. This would cause concurrently executed session wrappers to change the session key for all ongoing requests,
also for those that should be executed within a different session.

All graph element methods that perform operations on the graph accept the optional keyword arguments `transaction`,
`isolate`, and `pool`, which can override the defaults set by `execute_query`.

.. py:function:: execute_query(query, params={}, transaction=True, isolate=True, pool=None

The following examples use `eventlet` for concurrent querying:

.. literalinclude:: code/session_wrappers_conc.py
    :language: python
    :linenos:
