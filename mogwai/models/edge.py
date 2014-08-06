import logging
from mogwai._compat import array_types, integer_types, float_types, string_types, add_metaclass
from mogwai.connection import execute_query
from mogwai.exceptions import ElementDefinitionException, MogwaiQueryError, ValidationError
from mogwai.gremlin import GremlinMethod
from .element import Element, ElementMetaClass, edge_types

logger = logging.getLogger(__name__)


class EdgeMetaClass(ElementMetaClass):
    """Metaclass for edges."""

    def __new__(mcs, name, bases, body):
        #short circuit element_type inheritance
        body['label'] = body.pop('label', None)

        klass = super(EdgeMetaClass, mcs).__new__(mcs, name, bases, body)

        if not klass.__abstract__:
            label = klass.get_label()
            if label in edge_types and str(edge_types[label]) != str(klass):
                # Catch imports from other modules, don't reload module into vertex types, only load once
                logger.debug(ElementDefinitionException("%s is already registered as a edge: \n\tmcs: %s\n\tname: %s\n\tbases: %s\n\tbody: %s" % (label, mcs, name, bases, body)))
            else:
                edge_types[klass.get_label()] = klass
        return klass


@add_metaclass(EdgeMetaClass)
class Edge(Element):
    """Base class for all edges."""

    #__metaclass__ = EdgeMetaClass
    __abstract__ = True

    # if set to True, no more than one edge will
    # be created between two vertices
    __exclusive__ = False

    label = None

    gremlin_path = 'edge.groovy'

    _save_edge = GremlinMethod()
    _get_edges_between = GremlinMethod(classmethod=True)


    FACTORY_CLASS = None
    ## edge id
    ##edge_id = columns.UUID(save_strategy=columns.SAVE_ONCE)

    def __init__(self, outV, inV, **values):
        """
        Initialize this edge with the outgoing and incoming vertices as well as edge properties.

        :param outV: The vertex this edge is coming out of
        :type outV: Vertex
        :param inV: The vertex this edge is going into
        :type inV: Vertex
        :param values: The properties for this edge
        :type values: dict

        """
        self._outV = outV
        self._inV = inV
        super(Edge, self).__init__(**values)

    def __getstate__(self):
        state = {u'_id': self.id,
                 u'_type': u'edge',
                 u'_outV': str(self.outV().id),
                 u'_inV': str(self.inV().id),
                 u'_label': self.get_label(),
                 u'_properties': self.as_save_params()}
        return state

    def __setstate__(self, state):
        data = self.translate_db_fields(state)
        self.__init__(state['_outV'], state['_inV'], **data)
        return self

    @classmethod
    def find_by_value(cls, field, value, as_dict=False):
        """
        Returns edges that match the given field/value pair.

        :param field: The field to search
        :type field: str
        :param value: The value of the field
        :type value: str
        :param as_dict: Return results as a dictionary
        :type as_dict: boolean
        :rtype: [mogwai.models.Edge]
        """
        _field = cls.get_property_by_name(field)
        _label = cls.get_label()

        if isinstance(value, integer_types + float_types):
            search = 'filter{{it."{}" == {}}}'.format(_field, value)
        else:
            search = 'has("{}", "{}")'.format(_field, value)

        query = 'g.E("label","{}").{}.toList()'.format(_label, search)

        results = execute_query(query)

        objects = []
        for r in results:
            try:
                objects += [Element.deserialize(r)]
            except KeyError:  # pragma: no cover
                raise MogwaiQueryError('Edge type "%s" is unknown' % r.get('label', ''))

        if as_dict:  # pragma: no cover
            return {v._id: v for v in objects}

        return objects

    @classmethod
    def all(cls, ids, as_dict=False):
        """
        Load all edges with the given edge_ids from the graph. By default this will return a list of edges but if
        as_dict is True then it will return a dictionary containing edge_ids as keys and edges found as values.

        :param ids: A list of titan IDs
        :type ids: list
        :param as_dict: Toggle whether to return a dictionary or list
        :type as_dict: boolean
        :rtype: dict | list
        """
        if not isinstance(ids, array_types):
            raise MogwaiQueryError("ids must be of type list or tuple")

        strids = [str(i) for i in ids]
        qs = ['ids.collect{g.e(it)}']

        results = execute_query('\n'.join(qs), {'ids': strids})
        results = list(filter(None, results))

        if len(results) != len(ids):
            raise MogwaiQueryError("the number of results don't match the number of edge ids requested")

        objects = []
        for r in results:
            try:
                objects += [Element.deserialize(r)]
            except KeyError:  # pragma: no cover
                raise MogwaiQueryError('Edge type "%s" is unknown' % '')

        if as_dict:  # pragma: no cover
            return {e._id: e for e in objects}

        return objects

    @classmethod
    def get_label(cls):
        """
        Returns the label for this edge.

        :rtype: str

        """
        return cls._type_name(cls.label)

    @classmethod
    def get_between(cls, outV, inV, page_num=None, per_page=None):
        """
        Return all the edges with a given label between two vertices.

        :param outV: The vertex the edge comes out of.
        :type outV: Vertex
        :param inV: The vertex the edge goes into.
        :type inV: Vertex
        :param page_num: The page number of the results
        :type page_num: int
        :param per_page: The number of results per page
        :type per_page: int
        :rtype: list

        """
        return cls._get_edges_between(out_v=outV,
                                      in_v=inV,
                                      label=cls.get_label(),
                                      page_num=page_num,
                                      per_page=per_page)

    def validate(self):
        """
        Perform validation of this edge raising a ValidationError if any problems are encountered.
        """
        if self._id is None:
            if self._inV is None:
                raise ValidationError('in vertex must be set before saving new edges')
            if self._outV is None:
                raise ValidationError('out vertex must be set before saving new edges')
        super(Edge, self).validate()

    def save(self, *args, **kwargs):
        """
        Save this edge to the graph database.
        """
        super(Edge, self).save(*args, **kwargs)
        return self._save_edge(self._outV,
                               self._inV,
                               self.get_label(),
                               self.as_save_params(),
                               exclusive=self.__exclusive__)

    def _reload_values(self):
        """ Re-read the values for this edge from the graph database. """
        reloaded_values = {}
        results = execute_query('g.e(id)', {'id': self._id})
        if results:  # note this won't work if you update a node for titan pre-0.5.x, new id's are created
            #del results['_id']
            del results['_type']
            reloaded_values['_id'] = results['_id']
            for name, value in results.get('_properties', {}).items():
                reloaded_values[name] = value
            if results['_id']:
                setattr(self, '_id', results['_id'])
            return reloaded_values
        else:
            return {}

    @classmethod
    def get(cls, id):
        """
        Look up edge by titan assigned ID. Raises a DoesNotExist exception if a edge with the given edge id was not
        found. Raises a MultipleObjectsReturned exception if the edge_id corresponds to more than one edge in the graph.

        :param id: The titan assigned ID
        :type id: str | basestring
        :rtype: mogwai.models.Edge
        """
        try:
            results = cls.all([id])
            if len(results) > 1:  # pragma: no cover
                # This requires titan to be broken.
                raise cls.MultipleObjectsReturned

            result = results[0]
            if not isinstance(result, cls):
                raise cls.WrongElementType(
                    '%s is not an instance or subclass of %s' % (result.__class__.__name__, cls.__name__)
                )
            return result
        except MogwaiQueryError:
            raise cls.DoesNotExist

    @classmethod
    def create(cls, outV, inV, label=None, *args, **kwargs):
        """
        Create a new edge of the current type coming out of vertex outV and going into vertex inV with the given
        properties.

        :param outV: The vertex the edge is coming out of
        :type outV: Vertex
        :param inV: The vertex the edge is going into
        :type inV: Vertex

        """
        return super(Edge, cls).create(outV, inV, *args, **kwargs)

    def delete(self):
        """
        Delete the current edge from the graph.
        """
        if self.__abstract__:  # pragma: no cover
            raise MogwaiQueryError('cant delete abstract elements')
        if self._id is None:
            return self
        query = """
        e = g.e(id)
        if (e != null) {
          g.removeEdge(e)
          g.stopTransaction(SUCCESS)
        }
        """
        results = execute_query(query, {'id': self.id})

    def _simple_traversal(self, operation):
        """
        Perform a simple traversal starting from the current edge returning a list of results.

        :param operation: The operation to be performed
        :type operation: str
        :rtype: list

        """
        results = execute_query('g.e(id).%s()' % operation, {'id': self.id})
        return [Element.deserialize(r) for r in results]

    def inV(self):
        """
        Return the vertex that this edge goes into.

        :rtype: Vertex

        """
        from mogwai.models.vertex import Vertex

        if self._inV is None:
            self._inV = self._simple_traversal('inV')[0]
        if isinstance(self._inV, string_types + integer_types):
            self._inV = Vertex.get(self._inV)
        return self._inV

    def outV(self):
        """
        Return the vertex that this edge is coming out of.

        :rtype: Vertex

        """
        from mogwai.models.vertex import Vertex

        if self._outV is None:
            self._outV = self._simple_traversal('outV')[0]
        if isinstance(self._inV, string_types + integer_types):
            self._outV = Vertex.get(self._outV)
        return self._outV
