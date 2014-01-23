from __future__ import unicode_literals
import datetime
from pytz import utc
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
        """
        person -enrolled_in-> course
        course -taught_by-> person

        :param cls:
        :return:
        """
        super(BaseTraversalTestCase, cls).setUpClass()
        cls.jon = Person.create(name='Jon', age=143)
        cls.eric = Person.create(name='Eric', age=25)
        cls.blake = Person.create(name='Blake', age=14)

        cls.physics = Course.create(name='Physics 264', credits=1.0)
        cls.beekeeping = Course.create(name='Beekeeping', credits=15.0)
        cls.theoretics = Course.create(name='Theoretical Theoretics', credits=-3.5)

        cls.eric_in_physics = EnrolledIn.create(cls.eric, cls.physics,
                                                date_enrolled=datetime.datetime.now(tz=utc),
                                                enthusiasm=10)  # eric loves physics
        cls.jon_in_beekeeping = EnrolledIn.create(cls.jon, cls.beekeeping,
                                                  date_enrolled=datetime.datetime.now(tz=utc),
                                                  enthusiasm=1)  # jon hates beekeeping

        cls.blake_in_theoretics = EnrolledIn.create(cls.blake, cls.theoretics,
                                                    date_enrolled=datetime.datetime.now(tz=utc),
                                                    enthusiasm=8)

        cls.blake_beekeeping = TaughtBy.create(cls.beekeeping, cls.blake, overall_mood='Pedantic')
        cls.jon_physics = TaughtBy.create(cls.physics, cls.jon, overall_mood='Creepy')
        cls.eric_theoretics = TaughtBy.create(cls.theoretics, cls.eric, overall_mood='Obtuse')

    @classmethod
    def tearDownClass(cls):

        # reverse setup procedure and delete vertices and edges in graph
        cls.eric_theoretics.delete()
        cls.jon_physics.delete()
        cls.blake_beekeeping.delete()
        cls.blake_in_theoretics.delete()
        cls.jon_in_beekeeping.delete()
        cls.eric_in_physics.delete()
        cls.theoretics.delete()
        cls.beekeeping.delete()
        cls.physics.delete()
        cls.blake.delete()
        cls.eric.delete()
        cls.jon.delete()
        super(BaseTraversalTestCase, cls).tearDownClass()


@attr('unit', 'traversals')
class TestVertexTraversals(BaseTraversalTestCase):

    def test_inV_works(self):
        """Test that inV traversals work as expected"""
        results = self.jon.inV()
        self.assertEqual(len(results), 1)
        self.assertIn(self.physics, results)

        results = self.physics.inV()
        self.assertEqual(len(results), 1)
        self.assertIn(self.eric, results)

        results = self.eric.inV()
        self.assertEqual(len(results), 1)
        self.assertIn(self.theoretics, results)

        results = self.theoretics.inV()
        self.assertEqual(len(results), 1)
        self.assertIn(self.blake, results)

        results = self.beekeeping.inV()
        self.assertEqual(len(results), 1)
        self.assertIn(self.jon, results)

        results = self.blake.inV()
        self.assertEqual(len(results), 1)
        self.assertIn(self.beekeeping, results)

    def test_inE_traversals(self):
        """Test that inE traversals work as expected"""
        results = self.jon.inE()
        self.assertEqual(len(results), 1)
        self.assertIn(self.jon_physics, results)

    def test_outV_traversals(self):
        """Test that outV traversals work as expected"""
        results = self.eric.outV()
        self.assertEqual(len(results), 1)
        self.assertIn(self.physics, results)

    def test_outE_traverals(self):
        """Test that outE traversals work as expected"""
        results = self.blake.outE()
        self.assertEqual(len(results), 1)
        self.assertIn(self.blake_in_theoretics, results)

    def test_bothE_traversals(self):
        """Test that bothE traversals works"""
        results = self.jon.bothE()
        self.assertEqual(len(results), 2)
        self.assertIn(self.jon_physics, results)
        self.assertIn(self.jon_in_beekeeping, results)

    def test_bothV_traversals(self):
        """Test that bothV traversals work"""
        results = self.blake.bothV()
        self.assertEqual(len(results), 2)
        self.assertIn(self.beekeeping, results)


@attr('unit', 'traversals')
class TestVertexCentricQueries(BaseTraversalTestCase):

    def test_query_vertices(self):
        classes = self.jon.query().labels(EnrolledIn).direction(OUT).vertices()

    def test_query_in(self):
        people = self.physics.query().labels(EnrolledIn).direction(IN).vertices()
        for x in people:
            self.assertIsInstance(x, Person)

    def test_query_out_edges(self):
        classes = self.jon.query().labels(EnrolledIn).direction(OUT).edges()
        for x in classes:
            self.assertIsInstance(x, EnrolledIn, "Expected %s, got %s" % (type(EnrolledIn), type(x)))

    def test_two_labels(self):
        edges = self.jon.query().labels(EnrolledIn, TaughtBy).direction(BOTH).edges()
        for e in edges:
            self.assertIsInstance(e, (EnrolledIn, TaughtBy))

    def test_has(self):
        self.assertEqual(0, len(self.jon.query().labels(EnrolledIn).has('enrolledin_enthusiasm', 5,
                                                                        GREATER_THAN).vertices()))
        num = self.jon.query().labels(EnrolledIn).has('tests_vertex_traversals_tests_enthusiasm', 5, GREATER_THAN).count()
        self.assertEqual(0, num)

        self.assertEqual(1, len(self.jon.query().labels(EnrolledIn).has('enrolledin_enthusiasm', 5,
                                                                        LESS_THAN).vertices()))
        num = self.jon.query().labels(EnrolledIn).has('enrolledin_enthusiasm', 5, LESS_THAN).count()
        self.assertEqual(1, num)

    def test_interval(self):
        self.assertEqual(1, len(self.blake.query().labels(EnrolledIn).interval('enrolledin_enthusiasm', 2,
                                                                               9).vertices()))
        self.assertEqual(1, len(self.blake.query().labels(EnrolledIn).interval('enrolledin_enthusiasm', 9,
                                                                               2).vertices()))
        self.assertEqual(0, len(self.blake.query().labels(EnrolledIn).interval('enrolledin_enthusiasm', 2,
                                                                               8).vertices()))
