import inspect
import os.path
import time
import logging
from mogwai._compat import array_types, string_types, integer_types, float_types, iteritems

from mogwai.connection import execute_query
from mogwai.exceptions import MogwaiQueryError, MogwaiGremlinException
from .groovy import parse, GroovyImport


logger = logging.getLogger(__name__)


class BaseGremlinMethod(object):
    """ Maps a function in a groovy file to a method on a python class """

    def __init__(self,
                 path=None,
                 method_name=None,
                 classmethod=False,
                 property=False,
                 defaults={},
                 transaction=True,
                 imports=None):
        """
        Initialize the gremlin method and define how it is attached to class.

        :param path: Path to the gremlin source (relative to file class is defined in). Absolute paths work as well.
                     Defaults to gremlin.groovy.
        :type path: str
        :param method_name: The name of the function definition in the groovy file
        :type method_name: str
        :param classmethod: Method should behave as a classmethod if True
        :type classmethod: bool
        :param property: Method should behave as a property
        :type property: bool
        :param defaults: The default parameters to the function
        :type defaults: dict
        :param transaction: Close previous transaction before executing (True by default)
        :type transaction: bool
        :param imports: Additional imports to include when calling the GremlinMethod
        :type imports: list | tuple | str

        """
        self.is_configured = False
        self.is_setup = False
        self.path = path
        self.method_name = method_name
        self.classmethod = classmethod
        self.property = property
        self.defaults =defaults
        self.transaction = transaction

        # function
        self.attr_name = None
        self.arg_list = []
        self.function_body = None
        self.function_def = None

        # imports
        self.imports = None
        imports = imports or []
        if isinstance(imports, (str, string_types)):
            imports = [imports, ]
        self.extra_imports = imports

        #configuring attributes
        self.parent_class = None

    def configure_method(self, klass, attr_name, gremlin_path):
        """
        Sets up the methods internals

        :param klass: The class object this function is being added to
        :type klass: object
        :param attr_name: The attribute name this function will be added as
        :type attr_name: str
        :param gremlin_path: The path to the gremlin file containing method
        :type gremlin_path: str

        """
        if not self.is_configured:
            self.parent_class = klass
            self.attr_name = attr_name
            self.method_name = self.method_name or self.attr_name
            self.path = self.path or gremlin_path

            self.is_configured = True

    def _setup(self):
        """
        Does the actual method configuration, this is here because the method configuration must happen after the class
        is defined.
        """
        if not self.is_setup:

            #construct the default name
            name_func = getattr(self.parent_class, 'get_element_type', None) or \
                        getattr(self.parent_class, 'get_label', None)
            default_path = (name_func() if name_func else 'gremlin') + '.groovy'

            self.path = self.path or default_path
            if self.path.startswith('/'):
                path = self.path  # pragma: no cover
            else:
                path = inspect.getfile(self.parent_class)
                path = os.path.split(path)[0]
                path += '/' + self.path

            #TODO: make this less naive
            gremlin_obj = None
            file_def = parse(path)

            # Functions
            for grem_func in file_def.functions:
                if grem_func.name == self.method_name:
                    gremlin_obj = grem_func
                    break

            if gremlin_obj is None:
                raise MogwaiGremlinException("The method '%s' wasn't found in %s" % (self.method_name, path))

            for arg in gremlin_obj.args:
                if arg in self.arg_list:
                    raise MogwaiGremlinException("'%s' defined more than once in gremlin method arguments" % arg)
                self.arg_list.append(arg)

            self.function_body = gremlin_obj.body
            self.function_def = gremlin_obj.defn

            # imports
            self.imports = file_def.imports
            extra_imports = []
            for extra_import in self.extra_imports:
                extra_imports.append(GroovyImport([], [extra_import], ['import {};'.format(extra_import)]))
            self.extra_imports = extra_imports

            self.is_setup = True

    def __call__(self, instance, *args, **kwargs):
        """
        Intercept attempts to call the GremlinMethod attribute and perform a gremlin query returning the results.

        :param instance: The class instance the method was called on
        :type instance: object

        """
        self._setup()

        args = list(args)
        if not self.classmethod:
            args = [instance._id] + args

        params = self.defaults.copy()
        if len(args + list(kwargs.values())) > len(self.arg_list):  # pragma: no cover
            raise TypeError('%s() takes %s args, %s given' % (self.attr_name, len(self.arg_list), len(args)))

        #check for and calculate callable defaults
        for k, v in params.items():
            if callable(v):
                params[k] = v()

        arglist = self.arg_list[:]
        for arg in args:
            params[arglist.pop(0)] = arg

        for k, v in kwargs.items():
            if k not in arglist:
                an = self.attr_name
                if k in params:  # pragma: no cover
                    raise TypeError("%s() got multiple values for keyword argument '%s'" % (an, k))
                else:  # pragma: no cover
                    raise TypeError("%s() got an unexpected keyword argument '%s'" % (an, k))
            arglist.pop(arglist.index(k))
            params[k] = v

        params = self.transform_params_to_database(params)

        import_list = []
        for imp in self.imports + self.extra_imports:
            if imp is not None:
                for import_string in imp.import_list:
                    import_list.append(import_string)
        import_string = '\n'.join(import_list)

        script = '\n'.join([import_string, self.function_body])

        try:
            if hasattr(instance, 'get_element_type'):
                context = "vertices.{}".format(instance.get_element_type())
            elif hasattr(instance, 'get_label'):
                context = "edges.{}".format(instance.get_label())
            else:
                context = "other"

            context = "{}.{}".format(context, self.method_name)

            tmp = execute_query(script, params, transaction=self.transaction, context=context)
        except MogwaiQueryError as pqe:  # pragma: no cover
            import pprint
            msg = "Error while executing Gremlin method\n\n"
            msg += "[Method]\n{}\n\n".format(self.method_name)
            msg += "[Params]\n{}\n\n".format(pprint.pformat(params))
            msg += "[Function Body]\n{}\n".format(self.function_body)
            msg += "[Imports]\n{}\n".format(import_string)
            msg += "\n[Error]\n{}\n".format(pqe)
            if hasattr(pqe, 'raw_response'):
                msg += "\n[Raw Response]\n{}\n".format(pqe.raw_response)
            raise MogwaiGremlinException(msg)
        return tmp

    def transform_params_to_database(self, params):
        """
        Takes a dictionary of parameters and recursively translates them into parameters appropriate for sending over
        Rexpro.

        :param params: The parameters to be sent to the function
        :type params: dict
        :rtype: dict

        """
        import inspect
        from datetime import datetime
        from decimal import Decimal as _Decimal
        from uuid import UUID as _UUID
        from mogwai.models.element import BaseElement
        from mogwai.models import Edge, Vertex
        from mogwai.properties import DateTime, Decimal, UUID

        if isinstance(params, dict):
            return {k: self.transform_params_to_database(v) for k, v in iteritems(params)}
        if isinstance(params, array_types):
            return [self.transform_params_to_database(x) for x in params]
        if isinstance(params, BaseElement):
            return params._id
        if inspect.isclass(params) and issubclass(params, Edge):
            return params.label
        if inspect.isclass(params) and issubclass(params, Vertex):
            return params.element_type
        if isinstance(params, datetime):
            return DateTime().to_database(params)
        if isinstance(params, _UUID):
            return UUID().to_database(params)
        if isinstance(params, _Decimal):
            return Decimal().to_database(params)
        return params


class GremlinMethod(BaseGremlinMethod):
    """Gremlin method that returns a graph element"""

    @staticmethod
    def _deserialize(obj):
        """
        Recursively deserializes elements returned from rexster

        :param obj: The raw result returned from rexster
        :type obj: object

        """
        from mogwai.models.element import Element

        if isinstance(obj, dict) and '_id' in obj and '_type' in obj:
            return Element.deserialize(obj)
        elif isinstance(obj, dict):
            return {k: GremlinMethod._deserialize(v) for k, v in obj.items()}
        elif isinstance(obj, array_types):
            return [GremlinMethod._deserialize(v) for v in obj]
        else:
            return obj

    def __call__(self, instance, *args, **kwargs):
        results = super(GremlinMethod, self).__call__(instance, *args, **kwargs)
        return GremlinMethod._deserialize(results)


class GremlinValue(GremlinMethod):
    """Gremlin Method that returns one value"""

    def __call__(self, instance, *args, **kwargs):
        results = super(GremlinValue, self).__call__(instance, *args, **kwargs)

        if results is None:  # pragma: no cover
            return

        # we have to make a special case for dictionaries, python len returns number of keys,
        # even though it is one object. Don't do the same for lists or tuples, since they are
        # Gremlin Methods not GremlinValues.
        if isinstance(results, dict):
            return results
        if isinstance(results, integer_types + float_types + string_types):
            return results
        from mogwai.models.element import Element
        if isinstance(results, Element):
            return results

        if len(results) != 1:
            raise MogwaiGremlinException('GremlinValue requires a single value is returned (%s returned)' % len(results))
        return results[0]


class GremlinTable(GremlinMethod):  # pragma: no cover
    """Gremlin method that returns a table as its result"""

    def __call__(self, instance, *args, **kwargs):
        results = super(GremlinTable, self).__call__(instance, *args, **kwargs)
        if results is None:
            return
        return Table(results)
