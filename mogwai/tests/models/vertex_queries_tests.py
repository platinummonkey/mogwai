from __future__ import unicode_literals
from nose.plugins.attrib import attr

from mogwai.connection import MogwaiQueryError
from mogwai.tests.base import BaseMogwaiTestCase
from mogwai.models import Query, IN, OUT, Edge, Vertex, GREATER_THAN
from mogwai.properties import Integer, Double


class MockVertex(object):
    eid = 1


class MockVertex2(Vertex):
    age = Integer()


class MockEdge(Edge):
    age = Integer()
    fierceness = Double()


@attr('unit', 'query_vertex')
class SimpleQueryTest(BaseMogwaiTestCase):
    def setUp(self):
        self.q = Query(MockVertex())

    def test_limit(self):
        result = self.q.limit(10)._get_partial()
        self.assertEqual(result, "g.v(id).query().limit(limit)")

    def test_direction_in(self):
        result = self.q.direction(IN)._get_partial()
        self.assertEqual(result, "g.v(id).query().direction(IN)")

    def test_direction_out(self):
        result = self.q.direction(OUT)._get_partial()
        self.assertEqual(result, "g.v(id).query().direction(OUT)")

    def test_labels(self):
        result = self.q.labels('test')._get_partial()
        self.assertEqual(result, "g.v(id).query().labels('test')")
        # ensure the original wasn't modified
        self.assertListEqual(self.q._labels, [])

    def test_2labels(self):
        result = self.q.labels('test', 'test2')._get_partial()
        self.assertEqual(result, "g.v(id).query().labels('test', 'test2')")

    def test_object_label(self):
        result = self.q.labels(MockEdge)._get_partial()
        self.assertEqual(result, "g.v(id).query().labels('mock_edge')")

    def test_has(self):
        result = self.q.has(MockEdge.get_property_by_name("age"), 10)._get_partial()
        self.assertEqual(result, "g.v(id).query().has('mockedge_age', v0, Query.Compare.EQUAL)")

    def test_has_double_casting(self):
        result = self.q.has(MockEdge.get_property_by_name("fierceness"), 3.3)._get_partial()
        self.assertEqual(result, "g.v(id).query().has('mockedge_fierceness', v0 as double, Query.Compare.EQUAL)")

    def test_direction_except(self):
        with self.assertRaises(MogwaiQueryError):
            self.q.direction(OUT).direction(OUT)

    def test_has_double_casting_plain(self):
        result = self.q.has('fierceness', 3.3)._get_partial()
        self.assertEqual(result, "g.v(id).query().has('fierceness', v0 as double, Query.Compare.EQUAL)")

    def test_has_int(self):
        result = self.q.has('age', 21, GREATER_THAN)._get_partial()
        self.assertEqual(result, "g.v(id).query().has('age', v0, Query.Compare.GREATER_THAN)")

    def test_intervals(self):
        result = self.q.interval('age', 10, 20)._get_partial()
        self.assertEqual(result, "g.v(id).query().interval('age', v0, v1)")

    def test_double_interval(self):
        result = self.q.interval('fierceness', 2.5, 5.2)._get_partial()
        self.assertEqual(result, "g.v(id).query().interval('fierceness', v0 as double, v1 as double)")
