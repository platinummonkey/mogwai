.. _changelog:

ChangeLog
=========

Changes to the library are recorded here.

v0.7.3
------
 * Remove trace messages and clean-up developer logs

v0.7.1
------
 * Fixed Rexpro Connection Pooling connection soft-closing on exception
 * Fixed Relationship isolation bug (issue #10)

v0.7.0
------
 * BluePrints PartitionGraph support - thanks to Alex Olieman (aolieman)

v0.6.8
------
 * critical Relationships bugfix

v0.6.7
------
 * fixed GremlinTable method to return a new Table object that composes Row(s)

v0.6.6
------
 * find_by_value bugfix - thanks to Justin Hohner for identifying this bug.

v0.6.5
------
 * Proper connection closing bugfix - thanks to Elizabeth Ramirez

v0.6.4
------
 * Use blueprints element.setProperty method instead of deprecated addProperty - thanks to Kaisen Lin

v0.6.3
------
 * as_dict() method now includes element id

v0.6.2
------
 * Sane default __repr__ for Edges, feature parity to Vertex

v0.6.1
------
 * Save Strategy bugfix - thanks to Nick Vollmar

v0.6.0
------
 * Titan 0.5.0 support confirmed
 * Tests updated to reflect changes, do note running tests against this requires titan 0.5.0

v0.5.0
------
 * Python 3.3 and 3.4 compatibility - requires rexpro 0.3.0

v0.4.3
------
 * Added support for groovy imports on file level, as well as through GremlinMethod/GremlinValue (:ref:`See Example <example_groovy_imports>`)

v0.4.2
------
 * Added support for unknown properties and dictionary-like access (:ref:`See Example <example_unknown_properties>`)

v0.4.1
------
 * Missing import fix
 * setup.py typo fix

v0.4.0
------
 * Support concurrent connections via gevent and eventlet through rexpro support in the 0.2.0 release
 * All Properties support None when not required. Be aware when developing, especially around the Boolean property,
   since, when not required, it can actually be in 3 states (True, False and None) or (true, false and null in groovy)

v0.3.3
------
 * Fixed and improved find_by_value for both Edge and Vertex

v0.3.2
------
 * Fixed Circular Import
 * Fixed DateTime UTC bug
 * Wercker Integration
 * Documentation updates

v0.3.1
------
 * Bug Fixes
 * Documentation updates

v0.3.0
------
 * Utilize new rexpro.RexProConnectionPool
 * Includes new rexpro green-thread friendly gevent.socket RexProSockets

v0.2.13
-------
 * setup.py ``install_requires`` hot fix

v0.2.12
-------

 * Public CI preview

v0.2.11
-------

 * Documentation Updates


v0.2.10
-------

 * Minor bug fixes


v0.2.9
------

Serializable models via pickle.

.. code-block:: python

    import pickle

    vertex = MyTestVertex.create(name='test')
    serialized_vertex = pickle.dumps(vertex)
    deserialized_vertex = pickle.loads(serialized_vertex)
    assert vertex == deserialized_vertex


v0.2.8
------

Re-Release of Mogwai to the public. Name change to Mogwai, which loosely means "gremlin". This is a major refactor of the original `thunderdome` library by Blake.

 * Using RexPro, updated library to utilize RexPro and compatible with Titan 0.4.2
 * Refactored library, changed the way properties are handled, validated and their associated save strategies.
 * Removed vid and eid as primary keys, titan generates unique primary keys that we can utilize. Now accessible via Element._id or Element.id (the latter is a property shortcut to Element._id)
 * Added groovy tests, updated gremlin base method for new _type_name
 * Added interactive shell with some slight magic::

        Usage:
            python -m mogwai.shell --host localhost
        For more help see:
            python -m mogwai.shell --help
        Also HELP is available in the shell

 * Preview of index specification system, initial commit
 * Relationship system, includes generic query method, create relationship method and strict relationship checker
 * Fixed groovy files to only use local variables in core structure, will prevent Concurrent Global variable scope locks
 * Special Enum Vertex metaclass now available. ie. `MyVertex.MY_ENUM` will be able to resolve to an actual database entry
 * Performance monitoring tools now available - Customizable for different metric reporting mechanisms, ie, console, logs, graphite, newrelic.
 * Apache 2.0 License
