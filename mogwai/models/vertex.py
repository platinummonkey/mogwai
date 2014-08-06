from __future__ import unicode_literals
import inspect
import logging

from mogwai._compat import array_types, string_types, add_metaclass, integer_types, float_types
from mogwai.connection import execute_query
from mogwai.exceptions import MogwaiException, ElementDefinitionException, MogwaiQueryError
from mogwai.gremlin import GremlinMethod
from .element import Element, ElementMetaClass, vertex_types

logger = logging.getLogger(__name__)


class VertexMetaClass(ElementMetaClass):
    """Metaclass for vertices."""

    def __new__(mcs, name, bases, body):

        #short circuit element_type inheritance
        body['element_type'] = body.pop('element_type', None)

        klass = super(VertexMetaClass, mcs).__new__(mcs, name, bases, body)

        if not klass.__abstract__:
            element_type = klass.get_element_type()
            if element_type in vertex_types and str(vertex_types[element_type]) != str(klass):
                logger.debug(ElementDefinitionException("%s is already registered as a vertex: \n\tmcs: %s\n\tname: %s\n\tbases: %s\n\tbody: %s" % (element_type, mcs, name, bases, body)))
            else:
                vertex_types[element_type] = klass

            ##index requested indexed columns
            #klass._create_indices()

        return klass


class EnumVertexBaseMeta(VertexMetaClass):
    """
    This metaclass allows you to access MyVertexModel as if it were an enum.
    Ex. MyVertexModel.FOO

    The values are cached in a dictionary. This is useful if the number of MyVertexModels is small,
    however it it grows too large, you should be doing it a different way.

    This looks for a special (optional) function named `enum_generator` in your model and calls that
    to generate the ENUM for the model.

    There is an additional optional model attribute that can be set `__enum_id_only__` (defaults to True)
    which dictates whether or not just the Vertex ID is stored, or the whole Vertex in cache.
    """

    enums = None

    def __getattr__(cls, key):
        # property name to use for keying for the enum
        # method for handling name mangling, default to passthrough mode which subs spaces for underscores and caps
        store_model = getattr(cls, '__enum_id_only__', True)

        def get_enum_keyword(enum):
            return getattr(enum, 'enum_generator', lambda: (getattr(enum, 'name', '').replace(' ', '_').upper()))()

        if key.isupper():
            if cls.enums is None:
                cls.enums = dict(
                    [(get_enum_keyword(enum), enum._id if store_model else enum) for enum in cls.all()]
                )
            id = cls.enums.get(key, None)
            if not id:
                # make one attempt to load any new models
                cls.enums = dict(
                    [(get_enum_keyword(enum), enum._id if store_model else enum) for enum in cls.all()]
                )
                id = cls.enums.get(key, None)
                if not id:
                    raise AttributeError(key)
            return id
        else:
            return super(EnumVertexBaseMeta, cls).__getattr__(key)


@add_metaclass(VertexMetaClass)
class Vertex(Element):
    """ The Vertex model base class.

    The element type is auto-generated from the subclass name, but can optionally be set manually
    """
    #__metaclass__ = VertexMetaClass
    __abstract__ = True

    gremlin_path = 'vertex.groovy'

    _save_vertex = GremlinMethod()
    _traversal = GremlinMethod()
    _delete_related = GremlinMethod()

    element_type = None

    FACTORY_CLASS = None

    def __repr__(self):
        return "{}(element_type={}, id={}, values={})".format(self.__class__.__name__,
                                                              self.element_type,
                                                              getattr(self, '_id', None),
                                                              getattr(self, '_values', {}))

    def __getstate__(self):
        state = {'_id': self.id, '_type': 'vertex'}
        properties = self.as_save_params()
        properties['element_type'] = self.get_element_type()
        state['_properties'] = properties
        return state

    def __setstate__(self, state):
        self.__init__(**self.translate_db_fields(state))
        return self

    @classmethod
    def find_by_value(cls, field, value, as_dict=False):
        """
        Returns vertices that match the given field/value pair.

        :param field: The field to search
        :type field: str
        :param value: The value of the field
        :type value: str
        :param as_dict: Return results as a dictionary
        :type as_dict: boolean
        :rtype: [mogwai.models.Vertex]
        """
        _field = cls.get_property_by_name(field)
        _element_type = cls.get_element_type()

        if isinstance(value, integer_types + float_types):
            search = 'filter{{it."{}" == {}}}'.format(_field, value)
        else:
            search = 'has("{}", "{}")'.format(_field, value)

        query = 'g.V("element_type","{}").{}.toList()'.format(_element_type, search)

        results = execute_query(query)

        objects = []
        for r in results:
            try:
                objects += [Element.deserialize(r)]
            except KeyError:  # pragma: no cover
                raise MogwaiQueryError('Vertex type "%s" is unknown' % r.get('element_type', ''))

        if as_dict:  # pragma: no cover
            return {v._id: v for v in objects}

        return objects

    @classmethod
    def get_element_type(cls):
        """
        Returns the element type for this vertex.

        @returns: str

        """
        return cls._type_name(cls.element_type)

    @classmethod
    def all(cls, ids=[], as_dict=False, match_length=True):
        """
        Load all vertices with the given ids from the graph. By default this will return a list of vertices but if
        as_dict is True then it will return a dictionary containing ids as keys and vertices found as values.

        :param ids: A list of titan ids
        :type ids: list
        :param as_dict: Toggle whether to return a dictionary or list
        :type as_dict: boolean
        :rtype: dict | list

        """
        if not isinstance(ids, array_types):
            raise MogwaiQueryError("ids must be of type list or tuple")

        if len(ids) == 0:
            results = execute_query('g.V("element_type","%s").toList()' % cls.get_element_type())

        else:
            strids = [str(i) for i in ids]

            results = execute_query('ids.collect{g.v(it)}', {'ids': strids})
            results = list(filter(None, results))

            if len(results) != len(ids) and match_length:
                raise MogwaiQueryError("the number of results don't match the number of ids requested")

        objects = []
        for r in results:
            try:
                objects += [Element.deserialize(r)]
            except KeyError:  # pragma: no cover
                raise MogwaiQueryError('Vertex type "%s" is unknown' % r.get('element_type', ''))

        if as_dict:  # pragma: no cover
            return {v._id: v for v in objects}

        return objects

    def _reload_values(self):
        """
        Method for reloading the current vertex by reading its current values from the database.

        """
        reloaded_values = {}
        results = execute_query('g.v(id)', {'id': self._id})
        #del results['_id']
        del results['_type']
        reloaded_values['_id'] = results['_id']
        for name, value in results.get('_properties', {}).items():
            reloaded_values[name] = value
        return reloaded_values

    @classmethod
    def get(cls, id):
        """
        Look up vertex by its ID. Raises a DoesNotExist exception if a vertex with the given vid was not found.
        Raises a MultipleObjectsReturned exception if the vid corresponds to more than one vertex in the graph.

        :param id: The ID of the vertex
        :type id: str
        :rtype: mogwai.models.Vertex

        """
        try:
            results = cls.all([id])
            if len(results) > 1:  # pragma: no cover
                # This requires to titan to be broken.
                raise cls.MultipleObjectsReturned

            result = results[0]
            if not isinstance(result, cls):
                raise cls.WrongElementType(
                    '%s is not an instance or subclass of %s' % (result.__class__.__name__, cls.__name__)
                )
            return result
        except MogwaiQueryError as e:
            logger.exception(e)
            raise cls.DoesNotExist

    def save(self, *args, **kwargs):
        """
        Save the current vertex using the configured save strategy, the default save strategy is to re-save all
        fields every time the object is saved.
        """
        super(Vertex, self).save(*args, **kwargs)
        params = self.as_save_params()
        params['element_type'] = self.get_element_type()
        result = self._save_vertex(params)
        self._id = result._id
        for k, v in self._values.items():
            v.previous_value = result._values[k].previous_value
        return result

    def delete(self):
        """ Delete the current vertex from the graph. """
        if self.__abstract__:
            raise MogwaiQueryError('Cant delete abstract elements')
        if self._id is None:  # pragma: no cover
            return self
        query = """
        g.removeVertex(g.v(id))
        g.stopTransaction(SUCCESS)
        """
        results = execute_query(query, {'id': self._id})

    def _simple_traversal(self,
                          operation,
                          labels,
                          limit=None,
                          offset=None,
                          types=None):
        """
        Perform simple graph database traversals with ubiquitous pagination.

        :param operation: The operation to be performed
        :type operation: str
        :param labels: The edge labels to be used
        :type labels: list of Edges or strings
        :param start: The starting offset
        :type start: int
        :param max_results: The maximum number of results to return
        :type max_results: int
        :param types: The list of allowed result elements
        :type types: list

        """
        from mogwai.models.edge import Edge

        label_strings = []
        for label in labels:
            if inspect.isclass(label) and issubclass(label, Edge):
                label_string = label.get_label()
            elif isinstance(label, Edge):
                label_string = label.get_label()
            elif isinstance(label, string_types):
                label_string = label
            else:
                raise MogwaiException('traversal labels must be edge classes, instances, or strings')
            label_strings.append(label_string)

        allowed_elts = None
        if types is not None:
            allowed_elts = []
            for e in types:
                if issubclass(e, Vertex):
                    allowed_elts += [e.get_element_type()]
                elif issubclass(e, Edge):
                    allowed_elts += [e.get_label()]

        if limit is not None and offset is not None:
            start = offset
            end = offset + limit
        else:
            start = end = None

        return self._traversal(operation,
                               label_strings,
                               start,
                               end,
                               allowed_elts)

    def _simple_deletion(self, operation, labels):
        """
        Perform simple bulk graph deletion operation.

        :param operation: The operation to be performed
        :type operation: str
        :param labels: The edge label to be used
        :type labels: str or Edge

        """
        from mogwai.models.edge import Edge

        label_strings = []
        for label in labels:
            if inspect.isclass(label) and issubclass(label, Edge):
                label_string = label.get_label()
            elif isinstance(label, Edge):
                label_string = label.get_label()
            elif isinstance(label, string_types):
                label_string = label
            else:
                raise MogwaiException('traversal labels must be edge classes, instances, or strings')
            label_strings.append(label_string)

        return self._delete_related(operation, label_strings)

    def outV(self, *labels, **kwargs):
        """
        Return a list of vertices reached by traversing the outgoing edge with the given label.

        :param labels: pass in the labels to follow in as positional arguments
        :type labels: str or BaseEdge
        :param limit: The number of the page to start returning results at
        :type limit: int or None
        :param offset: The maximum number of results to return
        :type offset: int or None
        :param types: A list of allowed element types
        :type types: list

        """
        return self._simple_traversal('outV', labels, **kwargs)

    def inV(self, *labels, **kwargs):
        """
        Return a list of vertices reached by traversing the incoming edge with the given label.

        :param label: The edge label to be traversed
        :type label: str or BaseEdge
        :param limit: The number of the page to start returning results at
        :type limit: int or None
        :param offset: The maximum number of results to return
        :type offset: int or None
        :param types: A list of allowed element types
        :type types: list

        """
        return self._simple_traversal('inV', labels, **kwargs)

    def outE(self, *labels, **kwargs):
        """
        Return a list of edges with the given label going out of this vertex.

        :param label: The edge label to be traversed
        :type label: str or BaseEdge
        :param limit: The number of the page to start returning results at
        :type limit: int or None
        :param offset: The maximum number of results to return
        :type offset: int or None
        :param types: A list of allowed element types
        :type types: list

        """
        return self._simple_traversal('outE', labels, **kwargs)

    def inE(self, *labels, **kwargs):
        """
        Return a list of edges with the given label coming into this vertex.

        :param label: The edge label to be traversed
        :type label: str or BaseEdge
        :param limit: The number of the page to start returning results at
        :type limit: int or None
        :param offset: The maximum number of results to return
        :type offset: int or None
        :param types: A list of allowed element types
        :type types: list

        """
        return self._simple_traversal('inE', labels, **kwargs)

    def bothE(self, *labels, **kwargs):
        """
        Return a list of edges both incoming and outgoing from this vertex.

        :param label: The edge label to be traversed (optional)
        :type label: str or BaseEdge or None
        :param limit: The number of the page to start returning results at
        :type limit: int or None
        :param offset: The maximum number of results to return
        :type offset: int or None
        :param types: A list of allowed element types
        :type types: list

        """
        return self._simple_traversal('bothE', labels, **kwargs)

    def bothV(self, *labels, **kwargs):
        """
        Return a list of vertices both incoming and outgoing from this vertex.

        :param label: The edge label to be traversed (optional)
        :type label: str or BaseEdge or None
        :param limit: The number of the page to start returning results at
        :type limit: int or None
        :param offset: The maximum number of results to return
        :type offset: int or None
        :param types: A list of allowed element types
        :type types: list

        """
        return self._simple_traversal('bothV', labels, **kwargs)

    def delete_outE(self, *labels):
        """Delete all outgoing edges with the given label."""
        self._simple_deletion('outE', labels)

    def delete_inE(self, *labels):
        """Delete all incoming edges with the given label."""
        self._simple_deletion('inE', labels)

    def delete_outV(self, *labels):
        """Delete all outgoing vertices connected with edges with the given label."""
        self._simple_deletion('outV', labels)

    def delete_inV(self, *labels):
        """Delete all incoming vertices connected with edges with the given label."""
        self._simple_deletion('inV', labels)

    def query(self):
        from mogwai.models.query import Query
        return Query(self)
