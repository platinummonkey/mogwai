from __future__ import unicode_literals
import logging

from tornado.concurrent import Future

from mogwai._compat import float_types, print_
from mogwai import connection
from mogwai.exceptions import MogwaiQueryError
from .element import Element, EQUAL, NOT_EQUAL, GREATER_THAN, GREATER_THAN_EQUAL, LESS_THAN, LESS_THAN_EQUAL,\
    OUT, IN, BOTH, WITHIN
import copy
from mogwai.properties.base import GraphProperty

logger = logging.getLogger(__name__)


class Query(object):
    """
    All query operations return a new query object, which currently deviates from blueprints.
    The blueprints query object modifies and returns the same object
    This method seems more flexible, and consistent w/ the rest of Gremlin.
    """
    _limit = None

    def __init__(self, vertex):
        self._vertex = vertex
        self._has = []
        self._interval = []
        self._labels = []
        self._direction = []
        self._vars = {}

    def count(self, *args, **kwargs):
        """
        :returns: number of matching vertices
        :rtype: int
        """
        return self._execute('count', deserialize=False, **kwargs)

    def direction(self, direction):
        """
        :param direction: direction to compare or traverse
        :rtype: Query
        """
        q = copy.copy(self)
        if self._direction:
            raise MogwaiQueryError("Direction already set")
        q._direction = direction
        return q

    def edges(self, *args, **kwargs):
        """
        :rtype: list[edge.Edge]
        """
        return self._execute('', dir_element='E', **kwargs)

    def has(self, key, value, compare=EQUAL):
        """
        :param key: key to lookup
        :type key: str | mogwai.properties.GraphProperty
        :param value: value to compare
        :type value: str, float, int
        :param compare: comparison keyword
        :type compare: str
        :rtype: Query
        """
        q = copy.copy(self)
        #print_("Trying for key: %s with value: %s" % (key, value))
        if issubclass(type(key), property):
            logger.error("Use %s.get_property_by_name instead, this won't work" % self.__class__.__name__)
            raise MogwaiQueryError("Use %s.get_property_by_name instead, this won't work" % self.__class__.__name__)
        q._has.append((key, value, compare))
        return q

    def interval(self, key, start, end):
        """
        :rtype : Query
        """
        if start > end:
            start, end = end, start
        q = copy.copy(self)
        q._interval.append((key, start, end))
        return q

    def labels(self, *args):
        """
        :param args: list of Edges
        :type args: list[edge.Edge]
        :rtype: Query
        """
        tmp = []
        for x in args:
            try:
                tmp.append(x.get_label())
            except:
                tmp.append(x)

        q = copy.copy(self)
        q._labels = tmp
        return q

    def limit(self, limit):
        q = copy.copy(self)
        q._limit = limit
        return q

    def remove(self, *args, **kwargs):
        """ Deletes a vertex or edge """
        return self._execute('remove', deserialize=False, **kwargs)

    def vertexIds(self, *args, **kwargs):
        return self._execute('vertexIds', deserialize=False, **kwargs)

    def vertices(self, *args, **kwargs):
        return self._execute('', dir_element='', **kwargs)

    def _get_partial(self, dir_element=""):
        limit = ".limit(limit)" if self._limit else ""
        dir = ".{}{}()".format(self._direction, dir_element) if self._direction else ""

        # do labels
        labels = ""
        if self._labels:
            labels = ["'{}'".format(x) for x in self._labels]
            labels = ", ".join(labels)
            labels = ".hasLabel({})".format(labels)

        ### construct has clauses
        has = []

        for x in self._has:
            c = "v{}".format(len(self._vars))
            self._vars[c] = x[1]

            # not sure if necessary with new titan
            # val = "{} as double".format(c) if isinstance(x[1], float_types) else c
            key = x[0]
            has.append("has('{}', {}({}))".format(key, x[2], c))

        if has:
            tmp = ".".join(has)
            has = '.{}'.format(tmp)
        else:
            has = ""
        ### end construct has clauses

        intervals = []
        for x in self._interval:
            c = "v{}".format(len(self._vars))
            self._vars[c] = x[1]
            c2 = "v{}".format(len(self._vars))
            self._vars[c2] = x[2]

            # not sure if necessary
            # val1 = "{} as double".format(c) if isinstance(x[1], float_types) else c
            # val2 = "{} as double".format(c2) if isinstance(x[2], float_types) else c2

            tmp = "has('{}', {}({}, {}))".format(x[0], WITHIN, c, c2)
            intervals.append(tmp)

        if intervals:
            intervals = ".{}".format(".".join(intervals))
        else:
            intervals = ""

        return "g.V(id){}{}{}{}{}".format(labels, limit, dir, has, intervals)

    def _execute(self, func, deserialize=True, *args, **kwargs):
        dir_element = kwargs.get("dir_element", "")
        if func:
            func = ".{}()".format(func)
        tmp = "{}{}".format(self._get_partial(dir_element=dir_element), func)
        import ipdb; ipdb.set_trace()
        self._vars.update({"id": self._vertex._id, "limit": self._limit})

        def process_results(results):
            if deserialize:
                results = [Element.deserialize(r) for r in results]

        future_results = connection.execute_query(
            tmp, params=self._vars, handler=process_results, **kwargs)

        return future_results
