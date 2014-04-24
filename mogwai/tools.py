## TODO: Reference: Tooling from werkzeug tools - citation needed
from __future__ import unicode_literals
import sys
from mogwai._compat import reraise, string_types, PY2
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
