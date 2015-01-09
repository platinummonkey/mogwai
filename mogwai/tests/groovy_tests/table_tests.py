from __future__ import unicode_literals
import datetime
from pytz import utc
from uuid import uuid4
from nose.plugins.attrib import attr

from mogwai.exceptions import MogwaiGremlinException, MogwaiException
from mogwai.tests.base import BaseMogwaiTestCase

from mogwai.models import Vertex
from mogwai import properties
from mogwai import gremlin
from mogwai.gremlin.table import Table, Row
from mogwai._compat import print_
from copy import deepcopy
from collections import OrderedDict


class GroovyTestModel2(Vertex):

    element_type = 'groovy_test_model2'

    text = properties.Text()

    get_table_of_models = gremlin.GremlinTable(path='groovy_test_model.groovy', classmethod=True, defaults={'element_type': 'groovy_test_model2'})


@attr('unit', 'gremlin', 'gremlin_table')
class TestGremlinTable(BaseMogwaiTestCase):

    def test_method_loads_and_works(self):
        elements = []
        for i in range(10):
            elements.append(GroovyTestModel2.create(text='test{}'.format(i)))

        table = GroovyTestModel2.get_table_of_models()

        self.assertIsInstance(table, Table)
        self.assertEqual(10, len(table))
        for row in table:
            self.assertIsInstance(row, Row)
            self.assertTrue(row.text.startswith('test'))

        for element in elements:
            element.delete()


@attr('unit', 'gremlin', 'gremlin_table', 'gremlin_table_table')
class TestTableContainer(BaseMogwaiTestCase):

    def test_gremlin_table_row(self):
        d = OrderedDict({'test': 1, 'a': 'b', 'c': 3})
        r = Row(deepcopy(d))

        print_(r)

        self.assertDictEqual(d, r._Row__data)
        self.assertEqual(len(d), len(r))

        # test tuple-like access
        self.assertIn(r[0], d.values())
        self.assertListEqual(list(d.values()), list(r[:]))
        with self.assertRaises(MogwaiException):
            r[0] = 'test'

        with self.assertRaises(MogwaiException):
            r[:] = (1, 2, 3)

        with self.assertRaises(MogwaiException):
            del r[0]

        with self.assertRaises(MogwaiException):
            del r[0:2]

        # test dict-like access
        self.assertListEqual(list(d.values()), list(r.values()))
        self.assertListEqual(list(d.keys()), list(r.keys()))
        self.assertListEqual(list(d.items()), list(r.items()))
        self.assertEqual(d['test'], r['test'])
        self.assertEqual(d['a'], r['a'])
        self.assertEqual(d['c'], r['c'])
        with self.assertRaises(MogwaiException):
            r['test'] = 0

        with self.assertRaises(MogwaiException):
            del r['test']

        # test . notation access
        self.assertEqual(d['test'], r.test)
        self.assertEqual(d['a'], r.a)
        self.assertEqual(d['c'], r.c)
        with self.assertRaises(MogwaiException):
            r.test = 0
        with self.assertRaises(MogwaiException):
            del r.test

        # test iteration
        self.assertEqual(len(d), len([v for v in r]))
        self.assertListEqual(list(d.values()), [v for v in r])

        # test next
        self.assertIn(r.next(), d.values())
        self.assertIn(r.next(), d.values())
        self.assertIn(r.next(), d.values())

        # test equality
        r2 = Row(deepcopy(d))
        self.assertEqual(r, r2)

    def test_gremlin_table_table(self):
        data = [
            OrderedDict({'test': 1, 'a': 'b', 'c': 3}),
            OrderedDict({'test': 2, 'a': 'd', 'c': 5})
        ]
        t = Table(deepcopy(data))

        self.assertListEqual(data, t._Table__gremlin_result)

        # test iterator
        self.assertListEqual(data, [r._Row__data for r in t])

        # test tuple-like access
        self.assertIsInstance(t[0], Row)
        self.assertDictEqual(data[0], t[0]._Row__data)
        self.assertEqual(data[0]['test'], t[0].test)
        with self.assertRaises(MogwaiException):
            t[0] = 'test'
        with self.assertRaises(MogwaiException):
            del t[0]

        self.assertEqual(t[0], t.next())
        self.assertEqual(t[1], t.next())
