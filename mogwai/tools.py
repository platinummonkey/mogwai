## TODO: Reference: Tooling from werkzeug tools - citation needed
from __future__ import unicode_literals
import sys
from rexpro.exceptions import RexProConnectionException, RexProScriptException
from mogwai._compat import reraise, string_types, PY2
from mogwai import connection
from mogwai.exceptions import MogwaiBlueprintsWrapperException
from factory import base
import factory as factory


class ImportStringError(ImportError):
    """Provides information about a failed :func:`import_string` attempt."""

    # String in dotted notation that failed to be imported.
    import_name = None
    # Wrapped exception.
    exception = None

    def __init__(self, import_name, exception):
        self.import_name = import_name
        self.exception = exception

        msg = (
            'import_string() failed for %r. Possible reasons are:\n\n'
            '- missing __init__.py in a package;\n'
            '- package or module path not included in sys.path;\n'
            '- duplicated package or module name taking precedence in '
            'sys.path;\n'
            '- missing module, class, function or variable;\n\n'
            'Debugged import:\n\n%s\n\n'
            'Original exception:\n\n%s: %s')

        name = ''
        tracked = []
        for part in import_name.replace(':', '.').split('.'):
            name += (name and '.') + part
            imported = import_string(name, silent=True)
            if imported:
                tracked.append((name, getattr(imported, '__file__', None)))
            else:
                track = ['- %r found in %r.' % (n, i) for n, i in tracked]
                track.append('- %r not found.' % name)
                msg = msg % (import_name, '\n'.join(track),
                             exception.__class__.__name__, str(exception))
                break

        ImportError.__init__(self, msg)

    def __repr__(self):  # pragma: no cover
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.import_name,
                                 self.exception)


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    assert isinstance(import_name, string_types)
    # force the import name to automatically convert to strings
    import_name = str(import_name)
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        # __import__ is not able to handle unicode setup_strings in the fromlist
        # if the module is a package
        if PY2 and isinstance(obj, unicode):  # pragma: no cover
            obj = obj.encode('utf-8')
        try:
            return getattr(__import__(module, None, None, [obj]), obj)
        except (ImportError, AttributeError):
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            modname = module + '.' + obj
            __import__(modname)
            return sys.modules[modname]
    except ImportError as e:
        if not silent:
            reraise(
                ImportStringError,
                ImportStringError(import_name, e),
                sys.exc_info()[2])


class _Missing(object):

    def __repr__(self):  # pragma: no cover
        return 'no value'

    def __reduce__(self):  # pragma: no cover
        return '_missing'

_missing = _Missing()


class cached_property(object):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


class LazyImportClass(object):
    """ Lazily load and return a class """

    def __init__(self, import_name):
        try:
            self.__module__, self.__name__ = import_name.split('.', 1)
        except ValueError:  # pragma: no cover
            self.__module__ = ''
            self.__name__ = import_name
        self.__module__ = self.__module__ .lstrip('.')
        self.import_name = import_name.lstrip('.')
        #self.__setup_instantiated_vertex = getattr(self.klass, '__setup_instantiated_vertex')

    @cached_property
    def klass(self):
        """ Imports the class and caches """
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.klass(*args, **kwargs)

    def __setup_instantiated_vertex(self, *args, **kwargs):  # pragma: no cover
        return getattr(self.klass, '__setup_instantiated_vertex')(*args, **kwargs)


class Factory(base.Factory):
    """Factory for Mogwai models. """

    ABSTRACT_FACTORY = True

    _associated_model = None

    @classmethod
    def _load_target_class(cls, class_definition):
        """ So we can support potential circular import problems, by using normal import_string import specification.
        """
        associated_class = super(Factory, cls)._load_target_class(class_definition)

        if isinstance(associated_class, string_types) and '.' in associated_class:
            if cls._associated_model is None:
                cls._associated_model = import_string(associated_class)
                cls._associated_model.FACTORY_CLASS = cls
            return cls._associated_model

        if associated_class and associated_class.FACTORY_CLASS is None:
            associated_class.FACTORY_CLASS = cls

        return associated_class

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        from mogwai.models import Edge
        if issubclass(target_class.__class__, Edge):
            assert ('outV' in kwargs and 'inV' in kwargs), "Edges require in and out Vertices"
            obj = target_class.create(outV=kwargs.get('outV'), inV=kwargs.get('inV'), *args, **kwargs)
        else:
            obj = target_class.create(*args, **kwargs)
        return obj


class BlueprintsWrapper():
    """Abstract implementation for using a Blueprints graph wrapper
    within a persisted transaction. Within this transaction `g`
    refers to the wrapped graph.

    :param dict wrapper_configuration: the dict that defines which
        wrapper should be initialized, and with which configuration.
        `wrapper_configuration['class_name']` must be the Blueprints
        class name as a string.
        `wrapper_configuration['setup']` is an iterable with additional
        groovy statements that are executed upon initialization. It
        may be empty.
    :return: the used RexPro connection
    :raises MogwaiBlueprintsWrapperException: if no configuration is provided
    :raises RexProConnectionException: if the connection from the pool is closed
    """

    def __init__(self, wrapper_configuration=None):
        if not wrapper_configuration: # pragma: no cover
            raise MogwaiBlueprintsWrapperException("A wrapper configuration is required.")
        self.g_assignment = "g = new {}(g)".format(wrapper_configuration['class_name'])
        self.setup = wrapper_configuration['setup']

    def __enter__(self):
        # assign original execute_query()
        self.original_execute_query = connection.execute_query
        # open connection from pool
        self.connection = connection._connection_pool.create_connection()
        if not self.connection: # pragma: no cover
            raise RexProConnectionException("Cannot commit because connection was closed: %r" % (self.connection, ))
        self.connection.test_connection()
        self.connection.open_transaction()

        # shadow execute_query with self.connection and isolated=False
        def execute_with_connection(query, params={}, transaction=False, isolate=False, connection=self.connection, *args, **kwargs):
            return self.original_execute_query(
                query, params=params, transaction=False, isolate=False, connection=connection, *args, **kwargs
            )

        # patch execute_query to persist the transaction
        connection.execute_query = execute_with_connection

        # execute g_assignment
        resp = connection.execute_query(self.g_assignment)

        # provide a dummy stopTransaction() on non-transactional graphs
        connection.execute_query(
            "if (!g.metaClass.respondsTo(g, 'stopTransaction')) { g.metaClass.stopTransaction = {null} }"
        )

        # execute wrapper setup
        for statement in self.setup:
            connection.execute_query(statement)

        return self.connection

    def __exit__(self, exc, message, traceback):
        # execute g = g.baseGraph
        if exc is None:
            connection.execute_query("g = g.baseGraph")
        # replace original execute_query()
        connection.execute_query = self.original_execute_query
        # close connection
        try:
            self.connection.close_transaction(exc is None)
        except RexProScriptException: # pragma: no cover
            pass
        connection._connection_pool.close_connection(self.connection, soft=True)

        return False


class PartitionGraph(BlueprintsWrapper):
    """Wrapper for the Blueprints PartitionGraph, which is
    documented by https://github.com/tinkerpop/blueprints/wiki/Partition-Implementation

    :param str write: the default read+write partition.
    :param iterable read: optional read partitions.
    :return: the used RexPro connection
    :raises MogwaiBlueprintsWrapperException: if no write partition is provided
    """

    def __init__(self, write=None, read=[]):
        if not write: # pragma: no cover
            raise MogwaiBlueprintsWrapperException("A write partition is required.")
        self.g_assignment = "g = new PartitionGraph(g, '_partition', '{}')".format(write)
        self.setup = ["g.addReadPartition('{}')".format(rp) for rp in read]