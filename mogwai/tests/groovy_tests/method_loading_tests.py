from __future__ import unicode_literals
import datetime
from pytz import utc
from uuid import uuid4
from nose.plugins.attrib import attr

from mogwai.exceptions import MogwaiGremlinException
from mogwai.tests.base import BaseMogwaiTestCase

from mogwai.models import Vertex
from mogwai import properties
from mogwai import gremlin


class GroovyTestModel(Vertex):
    text = properties.Text()
    get_self = gremlin.GremlinMethod()
    cm_get_self = gremlin.GremlinMethod(method_name='get_self', classmethod=True)

    return_default = gremlin.GremlinValue(method_name='return_value', defaults={'val': lambda: 5000})
    return_list = gremlin.GremlinValue(property=1)
    return_value = gremlin.GremlinValue()

    arg_test1 = gremlin.GremlinValue()
    arg_test2 = gremlin.GremlinValue()


@attr('unit', 'gremlin')
class TestMethodLoading(BaseMogwaiTestCase):

    def test_method_loads_and_works(self):
        v1 = GroovyTestModel.create(text='cross fingers')

        v2 = v1.get_self()
        self.assertEqual(v1.id, v2.id)

        v3 = v1.cm_get_self(v1.id)
        self.assertEqual(v1.id, v3.id)

        v1.delete()


@attr('unit', 'gremlin', 'gremlin2')
class TestMethodArgumentHandling(BaseMogwaiTestCase):

    def test_callable_defaults(self):
        """
        Tests that callable default arguments are called
        """
        v1 = GroovyTestModel.create(text='cross fingers')
        self.assertEqual(v1.return_default(), 5000)
        v1.delete()

    def test_gremlin_value_enforces_single_object_returned(self):
        """
        Tests that a GremlinValue instance raises an error if more than one object is returned
        """
        v1 = GroovyTestModel.create(text='cross fingers')
        with self.assertRaises(MogwaiGremlinException):
            v1.return_list
        v1.delete()

    def test_type_conversion(self):
        """ Tests that the gremlin method converts certain python objects to their gremlin equivalents """
        v1 = GroovyTestModel.create(text='cross fingers')

        now = datetime.datetime.now(tz=utc)
        self.assertEqual(v1.return_value(now), properties.DateTime().to_database(now))

        uu = uuid4()
        self.assertEqual(v1.return_value(uu), properties.UUID().to_database(uu))
        v1.delete()

    def test_initial_arg_name_isnt_set(self):
        """ Tests that the name of the first argument in a instance method """
        v = GroovyTestModel.create(text='cross fingers')

        self.assertEqual(v, v.arg_test1())
        self.assertEqual(v, v.arg_test2())

        v.delete()
