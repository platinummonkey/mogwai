from __future__ import unicode_literals
import logging

from mogwai._compat import float_types, print_
from mogwai.connection import execute_query
from mogwai.exceptions import MogwaiQueryError
from .element import Element, EQUAL, NOT_EQUAL, GREATER_THAN, GREATER_THAN_EQUAL, LESS_THAN, LESS_THAN_EQUAL,\
    OUT, IN, BOTH
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

    def count(self):
        """
        :returns: number of matching vertices
        :rtype: int
        """
        return self._execute('count', deserialize=False)

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

    def edges(self):
        """
        :rtype: list[edge.Edge]
        """
        return self._execute('edges')

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
        compare = "Query.Compare.{}".format(compare)

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

    def remove(self):
        """ Deletes a vertex or edge """
        return self._execute('remove', deserialize=False)

    def vertexIds(self):
        return self._execute('vertexIds', deserialize=False)

    def vertices(self):
        return self._execute('vertices')

    def _get_partial(self):
        limit = ".limit(limit)" if self._limit else ""
        dir = ".direction({})".format(self._direction) if self._direction else ""

        # do labels
        labels = ""
        if self._labels:
            labels = ["'{}'".format(x) for x in self._labels]
            labels = ", ".join(labels)
            labels = ".labels({})".format(labels)

        ### construct has clauses
        has = []

        for x in self._has:
            c = "v{}".format(len(self._vars))
            self._vars[c] = x[1]

            val = "{} as double".format(c) if isinstance(x[1], float_types) else c
            key = x[0]
            has.append("has('{}', {}, {})".format(key, val, x[2]))

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


            val1 = "{} as double".format(c) if isinstance(x[1], float_types) else c
            val2 = "{} as double".format(c2) if isinstance(x[2], float_types) else c2

            tmp = "interval('{}', {}, {})".format(x[0], val1, val2)
            intervals.append(tmp)

        if intervals:
            intervals = ".{}".format(".".join(intervals))
        else:
            intervals = ""

        return "g.v(id).query(){}{}{}{}{}".format(labels, limit, dir, has, intervals)

    def _execute(self, func, deserialize=True):
        tmp = "{}.{}()".format(self._get_partial(), func)
        self._vars.update({"id": self._vertex._id, "limit": self._limit})
        results = execute_query(tmp, self._vars)

        if deserialize:
            return [Element.deserialize(r) for r in results]
        else:
            return results
