# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from tornado.testing import gen_test
from mogwai._compat import print_
from nose.plugins.attrib import attr

from mogwai import connection
from mogwai.exceptions import MogwaiException
from mogwai.tests.base import BaseMogwaiTestCase, TestVertexModel, TestEdgeModel, TestVertexModelDouble

from mogwai import gremlin
from mogwai import models
from mogwai.models import Edge, Vertex
from mogwai.models.vertex import EnumVertexBaseMeta
from mogwai import properties
from mogwai._compat import with_metaclass
from mogwai.exceptions import MogwaiQueryError


class TestVertexModel2(Vertex):
    name = properties.String(default='test_text')
    test_val = properties.Integer()


class OtherTestModel(Vertex):
    name = properties.Text(default='test_text')
    test_val = properties.Integer(default=3)


class AliasedTestModel(Vertex):
    name = properties.Text()
    test_val = properties.Integer(db_field='how_many')


class OtherTestEdge(Edge):
    test_val = properties.Integer(default=1)


class YetAnotherTestEdge(Edge):
    test_val = properties.Integer(default=2)


@attr('unit', 'vertex_io')
class TestVertexIO(BaseMogwaiTestCase):

    @gen_test
    def test_unicode_io(self):
        """
        Tests that unicode is saved and retrieved properly
        """
        tm1 = yield TestVertexModel.create(test_val=9, name=u'test2')
        try:
            self.assertEqual(tm1.name, u'test2')
            tm2 = yield TestVertexModel.get(tm1.id)
            self.assertEqual(tm1, tm2)
        finally:
            yield tm1.delete()

    @gen_test
    def test_model_save_and_load(self):
        """
        Tests that models can be saved and retrieved
        """
        tm0 = yield TestVertexModel.create(test_val=8, name='123456789')
        tm1 = yield TestVertexModel.create(test_val=9, name='456789')
        try:
            stream = yield TestVertexModel.all([tm0.id, tm1.id])
            tms = yield stream.read()

            self.assertEqual(len(tms), 2)

            for pname in tm0._properties.keys():
                self.assertEquals(getattr(tm0, pname), getattr(tms[0], pname))

            stream2 = yield TestVertexModel.all([tm1.id, tm0.id])
            tms = yield stream2.read()
            self.assertEqual(tms[0].id, tm1.id)
            self.assertEqual(tms[1].id, tm0.id)
        finally:
            yield tm0.delete()
            yield tm1.delete()

    @gen_test
    def test_model_updating_works_properly(self):
        """
        Tests that subsequent saves after initial model creation work
        """
        tm = yield TestVertexModel.create(test_val=8, name='123456789')
        try:
            tm.test_val = 100
            yield tm.save()

            tm.test_val = 80
            yield tm.save()

            tm.test_val = 60
            yield tm.save()

            tm.test_val = 40
            yield tm.save()

            tm.test_val = 20
            yield tm.save()

            tm2 = yield TestVertexModel.get(tm.id)

            self.assertEquals(tm.test_val, tm2.test_val)
        finally:
            yield tm.delete()

    @gen_test
    def test_model_deleting_works_properly(self):
        """
        Tests that an instance's delete method deletes the instance
        """
        tm = yield TestVertexModel.create(test_val=8, name='123456789')
        vid = tm.id
        yield tm.delete()
        # gremlinclient handler error handling needs to be fixed
        # with self.assertRaises(TestVertexModel.DoesNotExist):
        #     resp = yield TestVertexModel.get(vid)
        #     tm = yield resp.read()

    @gen_test
    def test_reload(self):
        """ Tests that and instance's reload method does an inplace update of the instance """
        tm0 = yield TestVertexModel.create(test_val=8, name='123456789')
        tm1 = yield TestVertexModel.get(tm0.id)
        try:
            tm1.test_val = 7
            yield tm1.save()

            yield tm0.reload()
            self.assertEqual(tm0.test_val, 7)
        finally:
            yield tm0.delete()

    @gen_test
    def test_reload_on_aliased_field(self):
        """ Tests that reload works with aliased fields """
        tm0 = yield AliasedTestModel.create(test_val=8, name='123456789')
        tm1 = yield AliasedTestModel.get(tm0.id)
        try:
            tm1.test_val = 7
            yield tm1.save()
            yield tm0.reload()
            self.assertEqual(tm0.test_val, 7)
        finally:
            yield tm1.delete()

    @gen_test
    def test_all_method(self):
        with self.assertRaises(MogwaiQueryError):
            yield TestVertexModel.all(1)

    @gen_test
    def test_all_method_invalid_length(self):
        v1 = yield TestVertexModel.create()
        v2 = yield TestVertexModel.create()
        try:
            from mogwai.exceptions import MogwaiQueryError
            with self.assertRaises(RuntimeError):
                stream = yield TestVertexModel.all([v1.id, v2.id, 'invalid'])
                yield stream.read()
        finally:
            yield v1.delete()
            yield v2.delete()

    @gen_test
    def test_find_by_value_method(self):
        v1 = yield TestVertexModel.create(name='v1', test_val=-99)
        v2 = yield TestVertexModel.create(name='v2', test_val=-99)
        v3 = yield TestVertexModelDouble.create(name='v3', test_val=-100.0)
        try:
            resp = yield TestVertexModel.find_by_value('name', 'v1')
            res1 = yield resp.read()
            self.assertEqual(len(res1), 1)
            resp = yield TestVertexModel.find_by_value('test_val', -99)
            res2 = yield resp.read()
            self.assertEqual(len(res2), 2)
            resp = yield TestVertexModel.find_by_value('name', 'bar')
            res3 = yield resp.read()
            self.assertIsNone(res3)
            resp = yield TestVertexModel.find_by_value('name', 'v1')
            res4 = yield resp.read()
            self.assertEqual(res4[0], v1)
            resp = yield TestVertexModelDouble.find_by_value('test_val', -100.0)
            res5 = yield resp.read()
            self.assertEqual(len(res5), 1)
        finally:
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()

    @gen_test
    def test_get_by_id(self):
        v1 = yield TestVertexModel.create()
        try:
            results = yield TestVertexModel.get(v1.id)
            self.assertIsInstance(results, TestVertexModel)
            self.assertEqual(results, v1)

            # Man, gremlinclient errors need some work
            # with self.assertRaises(TestEdgeModel.DoesNotExist):
            with self.assertRaises(RuntimeError):
                results = yield TestVertexModel.get(None)

            # with self.assertRaises(TestEdgeModel.DoesNotExist):
            with self.assertRaises(RuntimeError):
                results = yield TestVertexModel.get('nonexistant')

            v2 = yield TestVertexModel2.create(test_val=0)
            with self.assertRaises(TestVertexModel.WrongElementType):
                results = yield TestVertexModel.get(v2.id)
        finally:
            yield v2.delete()
            yield v1.delete()

    @gen_test
    @attr('vertex_delete_methods')
    def test_delete_methods(self):
        v1 = yield TestVertexModel.create()
        v2 = yield TestVertexModel.create()

        # delete_outE
        e1 = yield TestEdgeModel.create(v1, v2)
        yield v1.delete_outE(TestEdgeModel)

        # delete_inE
        e1 = yield TestEdgeModel.create(v1, v2)
        yield v2.delete_inE(TestEdgeModel)

        # delete_inV
        e1 = yield TestEdgeModel.create(v1, v2)
        yield v1.delete_inV(TestEdgeModel)

        # delete_outV
        v2 = yield TestVertexModel.create()
        e1 = yield TestEdgeModel.create(v1, v2)
        yield v2.delete_outV(TestEdgeModel)

        yield v2.delete()


class DeserializationTestModel(Vertex):
    count = properties.Integer()
    text = properties.Text()

    gremlin_path = 'deserialize.groovy'

    get_maps = gremlin.GremlinValue()
    get_list = gremlin.GremlinMethod()


@attr('unit', 'vertex_io')
class TestNestedDeserialization(BaseMogwaiTestCase):
    """
    Tests that vertices are properly deserialized when nested in map and list data structures
    """

    # @gen_test
    # def test_map_deserialization(self):
    #     """
    #     Tests that elements nested in maps are properly deserialized
    #     Not sure of the best approach for this, groovy associative arrays
    #     aren't deserialized as dicts
    #     """
    #     original = yield DeserializationTestModel.create(count=5, text='happy')
    #     nested = yield original.get_maps()
    #     nested = json.loads(nested)
    #     self.assertIsInstance(nested, dict)
    #     # self.assertEqual(nested['vertex'], original)
    #     self.assertEqual(nested['number'], 5)
    #     yield original.delete()

    @gen_test
    def test_list_deserialization(self):
        """
        Tests that elements nested in lists are properly deserialized
        """
        original = yield DeserializationTestModel.create(count=5, text='happy')
        try:
            stream = yield original.get_list()
            nested = yield stream.read()
            self.assertIsInstance(nested, list)
            self.assertEqual(nested[0], None)
            self.assertEqual(nested[1], 0)
            self.assertEqual(nested[2], 1)

            self.assertIsInstance(nested[3], list)
            self.assertEqual(nested[3][0], 2)
            self.assertEqual(nested[3][1], original)
            self.assertEqual(nested[3][2], 3)

            self.assertEqual(nested[4], 5)
        finally:
            yield original.delete()


class TestEnumVertexModel(with_metaclass(EnumVertexBaseMeta, Vertex)):
    __enum_id_only__ = False
    name = properties.String(default='test text')
    test_val = properties.Integer(default=0)

    def enum_generator(self):
        return '%s_%s' % (self.name.replace(' ', '_').upper(), self.test_val)


class TestEnumVertexModel2(with_metaclass(EnumVertexBaseMeta, Vertex)):
    name = properties.String(default='test text')
    test_val = properties.Integer(default=0)


# Enum has not been implemented
# @attr('unit', 'vertex_io', 'vertex_enum')
# class TestVertexEnumModel(BaseMogwaiTestCase):
#
#     @gen_test
#     def test_default_enum_handling(self):
#         """ Default enum handling test
#
#         Works by grabbing the `name` property and substituting ' ' for '_' and capitalizing
#         The enum returns the Vertex ID
#         """
#         tv = yield TestEnumVertexModel2.create()
#         txt = yield TestEnumVertexModel2.TEST_TEXT
#         self.assertEqual(txt, tv.id)
#         yield tv.delete()
#
#     def test_custom_enum_handling(self):
#         """ Custom enum handling test
#
#         Works utilizing the VertexModel's `enum_generator` instance method to generate the ENUMs
#         The enum returns the actual Vertex instance because the `__enum_id_only__` was set to False
#         which stores the entire Vertex instead of just the ID.
#         """
#         tv = TestEnumVertexModel.create()
#         self.assertEqual(TestEnumVertexModel.TEST_TEXT_0, tv)
#         tv.delete()
#
#     def test_attempt_load_fail(self):
#         with self.assertRaises(AttributeError):
#             TestEnumVertexModel.WRONG
#
#
@attr('unit', 'vertex_io')
class TestUpdateMethod(BaseMogwaiTestCase):

    @gen_test
    def test_success_case(self):
        """ Tests that the update method works as expected """
        tm = yield TestVertexModel.create(test_val=8, name='123456789')
        try:
            tm2 = yield tm.update(test_val=9)

            tm3 = yield TestVertexModel.get(tm.id)
            self.assertEqual(tm2.test_val, 9)
            self.assertEqual(tm3.test_val, 9)
        finally:
            yield tm.delete()

    @gen_test
    def test_unknown_names_raise_exception(self):
        """ Tests that passing in names for columns that don't exist raises an exception """
        tm = yield TestVertexModel.create(test_val=8, text='123456789')
        try:
            with self.assertRaises(TypeError):
                yield tm.update(jon='beard')
        finally:
            yield tm.delete()


@attr('unit', 'vertex_io')
class TestVertexTraversal(BaseMogwaiTestCase):

    @gen_test
    def test_outgoing_vertex_traversal(self):
        """Test that outgoing vertex traversals work."""
        v1 = yield TestVertexModel.create(test_val=1, name='Test1')
        v2 = yield TestVertexModel.create(test_val=2, name='Test2')
        v3 = yield OtherTestModel.create(test_val=3, name='Test3')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=12)
        e2 = yield TestEdgeModel.create(v1, v3, test_val=13)
        e3 = yield TestEdgeModel.create(v2, v3, test_val=14)
        try:
            stream = yield v1.outV(TestEdgeModel)
            results = yield stream.read()
            self.assertEqual(len(results), 2)
            self.assertIn(v2, results)
            self.assertIn(v3, results)

            stream = yield v1.outV(TestEdgeModel, types=[OtherTestModel])
            results = yield stream.read()
            self.assertEqual(len(results), 1)
            self.assertIn(v3, results)
        finally:
            yield e1.delete()
            yield e2.delete()
            yield e3.delete()
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()

    @gen_test
    def test_incoming_vertex_traversal(self):
        """Test that incoming vertex traversals work."""
        v1 = yield TestVertexModel.create(test_val=1, name='Test1')
        v2 = yield TestVertexModel.create(test_val=2, name='Test2')
        v3 = yield OtherTestModel.create(test_val=3, name='Test3')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=12)
        e2 = yield TestEdgeModel.create(v1, v3, test_val=13)
        e3 = yield TestEdgeModel.create(v2, v3, test_val=14)
        try:
            stream = yield v2.inV(TestEdgeModel)
            results = yield stream.read()
            self.assertEqual(len(results), 1)
            self.assertIn(v1, results)

            stream = yield v2.inV(TestEdgeModel, types=[OtherTestModel])
            results = yield stream.read()
            self.assertEqual(len(results), 0)
        finally:
            yield e1.delete()
            yield e2.delete()
            yield e3.delete()
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()

    @gen_test
    def test_outgoing_edge_traversals(self):
        """Test that outgoing edge traversals work."""
        v1 = yield TestVertexModel.create(test_val=1, name='Test1')
        v2 = yield TestVertexModel.create(test_val=2, name='Test2')
        v3 = yield OtherTestModel.create(test_val=3, name='Test3')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=12)
        e2 = yield TestEdgeModel.create(v1, v3, test_val=13)
        e3 = yield OtherTestEdge.create(v2, v3, test_val=14)
        try:
            stream = yield v2.outE()
            results = yield stream.read()
            self.assertEqual(len(results), 1)
            self.assertIn(e3, results)
            stream = yield v2.outE(types=[TestEdgeModel])
            results = yield stream.read()
            self.assertEqual(len(results), 0)
        finally:
            yield e1.delete()
            yield e2.delete()
            yield e3.delete()
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()

    @gen_test
    def test_incoming_edge_traversals(self):
        """Test that incoming edge traversals work."""
        v1 = yield TestVertexModel.create(test_val=1, name='Test1')
        v2 = yield TestVertexModel.create(test_val=2, name='Test2')
        v3 = yield OtherTestModel.create(test_val=3, name='Test3')
        e1 = yield TestEdgeModel.create(v1, v2, test_val=12)
        e2 = yield TestEdgeModel.create(v1, v3, test_val=13)
        e3 = yield OtherTestEdge.create(v2, v3, test_val=14)
        try:
            stream = yield v2.inE()
            results = yield stream.read()
            self.assertEqual(len(results), 1)
            self.assertIn(e1, results)
            stream = yield v2.inE(types=[OtherTestEdge])
            results = yield stream.read()
            self.assertEqual(len(results), 0)
        finally:
            yield e1.delete()
            yield e2.delete()
            yield e3.delete()
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()

    @gen_test
    def test_multiple_label_traversals(self):
        """ Tests that using multiple edges for traversals works """
        v1 = yield TestVertexModel.create(test_val=1, name='Test1')
        v2 = yield TestVertexModel.create(test_val=2, name='Test2')
        v3 = yield OtherTestModel.create(test_val=3, name='Test3')
        v4 = yield OtherTestModel.create(test_val=3, name='Test3')
        e1 = yield TestEdgeModel.create(v1, v2)
        e2 = yield OtherTestEdge.create(v1, v3)
        e3 = yield YetAnotherTestEdge.create(v1, v4)

        try:
            stream = yield v1.outV()
            results = yield stream.read()
            self.assertEqual(len(results), 3)

            stream = yield v1.outV(TestEdgeModel)
            results = yield stream.read()
            self.assertEqual(len(results), 1)

            stream = yield v1.outV(OtherTestEdge)
            results = yield stream.read()
            self.assertEqual(len(results), 1)

            stream = yield v1.outV(YetAnotherTestEdge)
            results = yield stream.read()
            self.assertEqual(len(results), 1)

            stream = yield v1.outV(TestEdgeModel, OtherTestEdge)
            out = yield stream.read()
            self.assertEqual(len(out), 2)
            self.assertIn(v2.id, [v.id for v in out])
            self.assertIn(v3.id, [v.id for v in out])

            stream = yield v1.outV(OtherTestEdge, YetAnotherTestEdge)
            out = yield stream.read()
            self.assertEqual(len(out), 2)
            self.assertIn(v3.id, [v.id for v in out])
            self.assertIn(v4.id, [v.id for v in out])
        finally:
            yield e1.delete()
            yield e2.delete()
            yield e3.delete()
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()
            yield v4.delete()

    @gen_test
    def test_multiple_edge_traversal_with_type_filtering(self):
        """ Tests that using multiple edges for traversals works """
        v = yield TestVertexModel.create(test_val=1, name='Test1')

        v1 = yield TestVertexModel.create()
        e1 = yield TestEdgeModel.create(v, v1)

        v2 = yield TestVertexModel.create()
        e2 = yield OtherTestEdge.create(v, v2)

        v3 = yield TestVertexModel.create()
        e3 = yield YetAnotherTestEdge.create(v, v3)

        v4 = yield OtherTestModel.create()
        e4 = yield TestEdgeModel.create(v, v4)

        v5 = yield OtherTestModel.create()
        e5 = yield OtherTestEdge.create(v, v5)

        v6 = yield OtherTestModel.create()
        e6 = yield YetAnotherTestEdge.create(v, v6)
        try:
            stream = yield v.outV()
            results = yield stream.read()
            self.assertEqual(len(results), 6)

            stream = yield v.outV(TestEdgeModel, OtherTestEdge)
            results = yield stream.read()
            self.assertEqual(len(results), 4)

            stream = yield v.outV(
                TestEdgeModel, OtherTestEdge, types=[TestVertexModel])
            results = yield stream.read()
            self.assertEqual(len(results), 2)
        finally:
            yield e1.delete()
            yield e2.delete()
            yield e3.delete()
            yield e4.delete()
            yield e5.delete()
            yield e6.delete()
            yield v.delete()
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()
            yield v4.delete()
            yield v5.delete()
            yield v6.delete()

    @gen_test
    def test_edge_instance_traversal_types(self):
        """ Test traversals with edge instances work properly """
        v1 = yield TestVertexModel.create(test_val=1, name='Test1')
        v2 = yield TestVertexModel.create(test_val=2, name='Test2')
        v3 = yield OtherTestModel.create(test_val=3, name='Test3')
        v4 = yield OtherTestModel.create(test_val=3, name='Test3')
        te = yield TestEdgeModel.create(v1, v2)
        ote = yield OtherTestEdge.create(v1, v3)
        yate = yield YetAnotherTestEdge.create(v1, v4)
        try:
            stream = yield v1.outV(te, ote)
            out = yield stream.read()
            self.assertEqual(len(out), 2)
            self.assertIn(v2.id, [v.id for v in out])
            self.assertIn(v3.id, [v.id for v in out])

            stream = yield v1.outV(ote, yate)
            out = yield stream.read()
            self.assertEqual(len(out), 2)
            self.assertIn(v3.id, [v.id for v in out])
            self.assertIn(v4.id, [v.id for v in out])
        finally:
            yield te.delete()
            yield ote.delete()
            yield yate.delete()
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()
            yield v4.delete()

    @gen_test
    def test_edge_label_string_traversal_types(self):
        """ Test traversals with edge instances work properly """
        v1 = yield TestVertexModel.create(test_val=1, name='Test1')
        v2 = yield TestVertexModel.create(test_val=2, name='Test2')
        v3 = yield OtherTestModel.create(test_val=3, name='Test3')
        v4 = yield OtherTestModel.create(test_val=3, name='Test3')
        e1 = yield TestEdgeModel.create(v1, v2)
        e2 = yield OtherTestEdge.create(v1, v3)
        e3 = yield YetAnotherTestEdge.create(v1, v4)
        try:
            stream = yield v1.outV(
                TestEdgeModel.get_label(), OtherTestEdge.get_label())
            out = yield stream.read()
            self.assertEqual(len(out), 2)
            self.assertIn(v2.id, [v.id for v in out])
            self.assertIn(v3.id, [v.id for v in out])

            stream = yield v1.outV(
                OtherTestEdge.get_label(), YetAnotherTestEdge.get_label())
            out = yield stream.read()
            self.assertEqual(len(out), 2)
            self.assertIn(v3.id, [v.id for v in out])
            self.assertIn(v4.id, [v.id for v in out])
        finally:
            yield e1.delete()
            yield e2.delete()
            yield e3.delete()
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()
            yield v4.delete()

    @gen_test
    def test_unknown_edge_traversal_filter_type_fails(self):
        """
        Tests an exception is raised if a traversal filter is
        used that's not an edge class, instance or label string fails
        """
        v1 = yield TestVertexModel.create(test_val=1, name='Test1')
        v2 = yield TestVertexModel.create(test_val=2, name='Test2')
        v3 = yield OtherTestModel.create(test_val=3, name='Test3')
        v4 = yield OtherTestModel.create(test_val=3, name='Test3')
        e1 = yield TestEdgeModel.create(v1, v2)
        e2 = yield OtherTestEdge.create(v1, v3)
        e3 = yield YetAnotherTestEdge.create(v1, v4)
        try:
            with self.assertRaises(MogwaiException):
                out = v1.outV(5)

            with self.assertRaises(MogwaiException):
                out = v1.outV(True)
        finally:
            yield e1.delete()
            yield e2.delete()
            yield e3.delete()
            yield v1.delete()
            yield v2.delete()
            yield v3.delete()
            yield v4.delete()

    @gen_test
    @attr('manual_properties')
    def test_manual_properties(self):
        v = yield TestVertexModel.create(test_val=1, name='Test 7', some_property=32)
        try:
            print_("Got Results: {}".format(v))
            print_("Result dict: {}".format(v.as_dict()))
            print_("\tResult properties: {}".format(v._properties.keys()))
            print_("\tResult Manaul: {}".format(v._manual_values.items()))

            self.assertEqual(v['some_property'], 32)
            self.assertIn('some_property', v)  # This also tests __contains__
            self.assertIn('test_val', v)  # This also tests __contains__

            # test len(Element()), should return len(element._properties) + len(element._manual_values)
            self.assertEqual(len(v), 3)

            # test __iter__
            prop_keys = [key for key in v]
            self.assertEqual(len(prop_keys), 3)
            for prop_key in v:
                self.assertIn(prop_key, ['test_val', 'name', 'some_property'])

            # test keys()
            self.assertEqual(len(prop_keys), len(v.keys()))
            for prop_key in v.keys():
                self.assertIn(prop_key, prop_keys)

            # test values()
            prop_values = v.values()
            self.assertEqual(len(prop_values), 3)
            for prop_value in prop_values:
                self.assertIn(prop_value, [1, 'Test 7', 32])

            # test items()
            prop_items = v.items()
            self.assertEqual(len(prop_items), 3)
            for prop_key, prop_value in prop_items:
                self.assertIn(prop_key, ['test_val', 'name', 'some_property'])
                self.assertIn(prop_value, [1, 'Test 7', 32])

            # test change
            v['some_property'] = 42
            self.assertEqual(v['some_property'], 42)
            yield v.save()
            self.assertEqual(v['some_property'], 42)

            # test delete
            del v['some_property']
            # This should still exist, so the property can be removed from the database,
            # but should raise an AttributeError if attempted to access normally
            self.assertIn('some_property', v)
            self.assertIsNone(v._manual_values.get('some_property'))
            with self.assertRaises(AttributeError):
                value = v['some_property']
                print_("Got value: {}".format(value))
        finally:
            yield v.delete()
