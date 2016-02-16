from __future__ import unicode_literals
import datetime
from pytz import utc

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.testing import gen_test

from nose.plugins.attrib import attr

from mogwai.tests.base import BaseMogwaiTestCase

from mogwai.models import Vertex, Edge, IN, OUT, BOTH, GREATER_THAN, LESS_THAN
from mogwai import properties


# Vertices
class Person(Vertex):
    name = properties.Text()
    age = properties.Integer()


class Course(Vertex):
    name = properties.Text()
    credits = properties.Decimal()


# Edges
class EnrolledIn(Edge):
    date_enrolled = properties.DateTime()
    enthusiasm = properties.Integer(default=5)  # medium, 1-10, 5 by default


class TaughtBy(Edge):
    overall_mood = properties.Text(default='Grumpy')


class BaseTraversalTestCase(BaseMogwaiTestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseTraversalTestCase, cls).setUpClass()
        loop = IOLoop.current()
        @gen.coroutine
        def build_graph():
            """
            person -enrolled_in-> course
            course -taught_by-> person

            :param cls:
            :return:
            """
            cls.jon = yield Person.create(name='Jon', age=143)
            cls.eric = yield Person.create(name='Eric', age=25)
            cls.blake = yield Person.create(name='Blake', age=14)

            cls.physics = yield Course.create(name='Physics 264', credits=1.0)
            cls.beekeeping = yield Course.create(name='Beekeeping', credits=15.0)
            cls.theoretics = yield Course.create(name='Theoretical Theoretics', credits=-3.5)

            cls.eric_in_physics = yield EnrolledIn.create(cls.eric, cls.physics,
                                                    date_enrolled=datetime.datetime.now(tz=utc),
                                                    enthusiasm=10)  # eric loves physics
            cls.jon_in_beekeeping = yield EnrolledIn.create(cls.jon, cls.beekeeping,
                                                      date_enrolled=datetime.datetime.now(tz=utc),
                                                      enthusiasm=1)  # jon hates beekeeping

            cls.blake_in_theoretics = yield EnrolledIn.create(cls.blake, cls.theoretics,
                                                        date_enrolled=datetime.datetime.now(tz=utc),
                                                        enthusiasm=8)

            cls.blake_beekeeping = yield TaughtBy.create(cls.beekeeping, cls.blake, overall_mood='Pedantic')
            cls.jon_physics = yield TaughtBy.create(cls.physics, cls.jon, overall_mood='Creepy')
            cls.eric_theoretics = yield TaughtBy.create(cls.theoretics, cls.eric, overall_mood='Obtuse')
        loop.run_sync(build_graph)

    @classmethod
    def tearDownClass(cls):
        loop = IOLoop.current()
        @gen.coroutine
        def destroy_graph():
            # reverse setup procedure and delete vertices and edges in graph
            yield cls.eric_theoretics.delete()
            yield cls.jon_physics.delete()
            yield cls.blake_beekeeping.delete()
            yield cls.blake_in_theoretics.delete()
            yield cls.jon_in_beekeeping.delete()
            yield cls.eric_in_physics.delete()
            yield cls.theoretics.delete()
            yield cls.beekeeping.delete()
            yield cls.physics.delete()
            yield cls.blake.delete()
            yield cls.eric.delete()
            yield cls.jon.delete()
        loop.run_sync(destroy_graph)
        super(BaseTraversalTestCase, cls).tearDownClass()


@attr('unit', 'traversals')
class TestVertexTraversals(BaseTraversalTestCase):

    @gen_test
    def test_inV_works(self):
        """Test that inV traversals work as expected"""

        stream = yield self.jon.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.physics, results)

        stream = yield self.physics.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.eric, results)

        stream = yield self.eric.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.theoretics, results)

        stream = yield self.theoretics.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.blake, results)

        stream = yield self.beekeeping.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.jon, results)

        stream = yield self.blake.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.beekeeping, results)

    @gen_test
    def test_inE_traversals(self):
        """Test that inE traversals work as expected"""
        stream = yield self.jon.inE()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.jon_physics, results)

    @gen_test
    def test_outV_traversals(self):
        """Test that outV traversals work as expected"""
        stream = yield self.eric.outV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.physics, results)

    @gen_test
    def test_outE_traverals(self):
        """Test that outE traversals work as expected"""
        stream = yield self.blake.outE()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.blake_in_theoretics, results)

    @gen_test
    def test_bothE_traversals(self):
        """Test that bothE traversals works"""
        stream = yield self.jon.bothE()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.jon_physics, results)
        self.assertIn(self.jon_in_beekeeping, results)

    @gen_test
    def test_bothV_traversals(self):
        """Test that bothV traversals work"""
        stream = yield self.blake.bothV()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.beekeeping, results)

#
# @attr('unit', 'traversals')
# class TestVertexCentricQueries(BaseTraversalTestCase):
#
#     @gen_test
#     def test_query_vertices(self):
#         stream = yield self.jon.query().direction(OUT).labels(EnrolledIn).vertices()
#         results = yield stream.read()
#         print(results)
#
#     def test_query_in(self):
#         people = self.physics.query().labels(EnrolledIn).direction(IN).vertices()
#         for x in people:
#             self.assertIsInstance(x, Person)
#
#     def test_query_out_edges(self):
#         classes = self.jon.query().labels(EnrolledIn).direction(OUT).edges()
#         for x in classes:
#             self.assertIsInstance(x, EnrolledIn, "Expected %s, got %s" % (type(EnrolledIn), type(x)))
#
#     def test_two_labels(self):
#         edges = self.jon.query().labels(EnrolledIn, TaughtBy).direction(BOTH).edges()
#         for e in edges:
#             self.assertIsInstance(e, (EnrolledIn, TaughtBy))
#
#     def test_has(self):
#         self.assertEqual(0, len(self.jon.query().labels(EnrolledIn).has('enrolledin_enthusiasm', 5,
#                                                                         GREATER_THAN).vertices()))
#         num = self.jon.query().labels(EnrolledIn).has('tests_vertex_traversals_tests_enthusiasm', 5, GREATER_THAN).count()
#         self.assertEqual(0, num)
#
#         self.assertEqual(1, len(self.jon.query().labels(EnrolledIn).has('enrolledin_enthusiasm', 5,
#                                                                         LESS_THAN).vertices()))
#         num = self.jon.query().labels(EnrolledIn).has('enrolledin_enthusiasm', 5, LESS_THAN).count()
#         self.assertEqual(1, num)
#
#     def test_interval(self):
#         self.assertEqual(1, len(self.blake.query().labels(EnrolledIn).interval('enrolledin_enthusiasm', 2,
#                                                                                9).vertices()))
#         self.assertEqual(1, len(self.blake.query().labels(EnrolledIn).interval('enrolledin_enthusiasm', 9,
#                                                                                2).vertices()))
#         self.assertEqual(0, len(self.blake.query().labels(EnrolledIn).interval('enrolledin_enthusiasm', 2,
#                                                                                8).vertices()))
