# -*- coding: utf-8 -*-
from __future__ import unicode_literals
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

    def test_unicode_io(self):
        """
        Tests that unicode is saved and retrieved properly
        """
        tm1 = TestVertexModel.create(test_val=9, name=u'test2')
        tm2 = TestVertexModel.get(tm1._id)
        tm1.delete()

    def test_model_save_and_load(self):
        """
        Tests that models can be saved and retrieved
        """
        tm0 = TestVertexModel.create(test_val=8, name='123456789')
        tm1 = TestVertexModel.create(test_val=9, name='456789')
        tms = TestVertexModel.all([tm0.id, tm1.id])

        self.assertEqual(len(tms), 2)

        for pname in tm0._properties.keys():
            self.assertEquals(getattr(tm0, pname), getattr(tms[0], pname))

        tms = TestVertexModel.all([tm1.id, tm0.id])
        self.assertEqual(tms[0].id, tm1.id)
        self.assertEqual(tms[1].id, tm0.id)

        tm0.delete()
        tm1.delete()

    def test_model_updating_works_properly(self):
        """
        Tests that subsequent saves after initial model creation work
        """
        tm = TestVertexModel.create(test_val=8, name='123456789')

        tm.test_val = 100
        tm.save()

        tm.test_val = 80
        tm.save()

        tm.test_val = 60
        tm.save()

        tm.test_val = 40
        tm.save()

        tm.test_val = 20
        tm.save()

        tm2 = TestVertexModel.get(tm.id)
        self.assertEquals(tm.test_val, tm2.test_val)
        tm.delete()

    def test_model_deleting_works_properly(self):
        """
        Tests that an instance's delete method deletes the instance
        """
        tm = TestVertexModel.create(test_val=8, name='123456789')
        vid = tm.id
        tm.delete()
        with self.assertRaises(TestVertexModel.DoesNotExist):
            tm2 = TestVertexModel.get(vid)

    def test_reload(self):
        """ Tests that and instance's reload method does an inplace update of the instance """
        tm0 = TestVertexModel.create(test_val=8, name='123456789')
        tm1 = TestVertexModel.get(tm0.id)
        tm1.test_val = 7
        tm1.save()

        tm0.reload()
        self.assertEqual(tm0.test_val, 7)
        tm0.delete()

    def test_reload_on_aliased_field(self):
        """ Tests that reload works with aliased fields """
        tm0 = AliasedTestModel.create(test_val=8, name='123456789')
        tm1 = AliasedTestModel.get(tm0.id)
        tm1.test_val = 7
        tm1.save()

        tm0.reload()
        self.assertEqual(tm0.test_val, 7)
        tm1.delete()

    def test_all_method(self):
        with self.assertRaises(MogwaiQueryError):
            TestVertexModel.all(1)

    def test_all_method_invalid_length(self):
        v1 = TestVertexModel.create()
        v2 = TestVertexModel.create()
        from mogwai.exceptions import MogwaiQueryError
        with self.assertRaises(MogwaiQueryError):
            TestVertexModel.all([v1.id, v2.id, 'invalid'])
        v1.delete()
        v2.delete()

    def test_find_by_value_method(self):
        v1 = TestVertexModel.create(name='v1', test_val=-99)
        v2 = TestVertexModel.create(name='v2', test_val=-99)
        v3 = TestVertexModelDouble.create(name='v3', test_val=-100.0)

        self.assertEqual(len(TestVertexModel.find_by_value('name', 'v1')), 1)
        self.assertEqual(len(TestVertexModel.find_by_value('test_val', -99)), 2)
        self.assertEqual(len(TestVertexModel.find_by_value('name', 'bar')), 0)

        self.assertEqual(TestVertexModel.find_by_value('name', 'v1')[0], v1)

        self.assertEqual(len(TestVertexModelDouble.find_by_value('test_val', -100.0)), 1)
        v1.delete()
        v2.delete()
        v3.delete()

    def test_get_by_id(self):
        v1 = TestVertexModel.create()
        results = TestVertexModel.get(v1.id)
        self.assertIsInstance(results, TestVertexModel)
        self.assertEqual(results, v1)

        with self.assertRaises(TestEdgeModel.DoesNotExist):
            results = TestVertexModel.get(None)

        with self.assertRaises(TestEdgeModel.DoesNotExist):
            results = TestVertexModel.get('nonexistant')

        v2 = TestVertexModel2.create(test_val=0)
        with self.assertRaises(TestVertexModel.WrongElementType):
            results = TestVertexModel.get(v2.id)

        v2.delete()
        v1.delete()

    @attr('vertex_delete_methods')
    def test_delete_methods(self):
        v1 = TestVertexModel.create()
        v2 = TestVertexModel.create()

        # delete_outE
        e1 = TestEdgeModel.create(v1, v2)
        v1.delete_outE(TestEdgeModel)

        # delete_inE
        e1 = TestEdgeModel.create(v1, v2)
        v2.delete_inE(TestEdgeModel)

        # delete_inV
        e1 = TestEdgeModel.create(v1, v2)
        v1.delete_inV(TestEdgeModel)

        # delete_outV
        v2 = TestVertexModel.create()
        e1 = TestEdgeModel.create(v1, v2)
        v2.delete_outV(TestEdgeModel)

        v2.delete()


class DeserializationTestModel(Vertex):
    count = properties.Integer()
    text = properties.Text()

    gremlin_path = 'deserialize.groovy'

    get_map = gremlin.GremlinValue()
    get_list = gremlin.GremlinMethod()


@attr('unit', 'vertex_io')
class TestNestedDeserialization(BaseMogwaiTestCase):
    """
    Tests that vertices are properly deserialized when nested in map and list data structures
    """

    def test_map_deserialization(self):
        """
        Tests that elements nested in maps are properly deserialized
        """

        original = DeserializationTestModel.create(count=5, text='happy')
        nested = original.get_map()

        self.assertIsInstance(nested, dict)
        self.assertEqual(nested['vertex'], original)
        self.assertEqual(nested['number'], 5)
        original.delete()

    def test_list_deserialization(self):
        """
        Tests that elements nested in lists are properly deserialized
        """

        original = DeserializationTestModel.create(count=5, text='happy')
        nested = original.get_list()

        self.assertIsInstance(nested, list)
        self.assertEqual(nested[0], None)
        self.assertEqual(nested[1], 0)
        self.assertEqual(nested[2], 1)

        self.assertIsInstance(nested[3], list)
        self.assertEqual(nested[3][0], 2)
        self.assertEqual(nested[3][1], original)
        self.assertEqual(nested[3][2], 3)

        self.assertEqual(nested[4], 5)
        original.delete()


class TestEnumVertexModel(with_metaclass(EnumVertexBaseMeta, Vertex)):
    __enum_id_only__ = False
    name = properties.String(default='test text')
    test_val = properties.Integer(default=0)

    def enum_generator(self):
        return '%s_%s' % (self.name.replace(' ', '_').upper(), self.test_val)


class TestEnumVertexModel2(with_metaclass(EnumVertexBaseMeta, Vertex)):
    name = properties.String(default='test text')
    test_val = properties.Integer(default=0)


@attr('unit', 'vertex_io', 'vertex_enum')
class TestVertexEnumModel(BaseMogwaiTestCase):

    def test_default_enum_handling(self):
        """ Default enum handling test

        Works by grabbing the `name` property and substituting ' ' for '_' and capitalizing
        The enum returns the Vertex ID
        """
        tv = TestEnumVertexModel2.create()
        self.assertEqual(TestEnumVertexModel2.TEST_TEXT, tv.id)
        tv.delete()

    def test_custom_enum_handling(self):
        """ Custom enum handling test

        Works utilizing the VertexModel's `enum_generator` instance method to generate the ENUMs
        The enum returns the actual Vertex instance because the `__enum_id_only__` was set to False
        which stores the entire Vertex instead of just the ID.
        """
        tv = TestEnumVertexModel.create()
        self.assertEqual(TestEnumVertexModel.TEST_TEXT_0, tv)
        tv.delete()

    def test_attempt_load_fail(self):
        with self.assertRaises(AttributeError):
            TestEnumVertexModel.WRONG


@attr('unit', 'vertex_io')
class TestUpdateMethod(BaseMogwaiTestCase):
    def test_success_case(self):
        """ Tests that the update method works as expected """
        tm = TestVertexModel.create(test_val=8, name='123456789')
        tm2 = tm.update(test_val=9)

        tm3 = TestVertexModel.get(tm.id)
        self.assertEqual(tm2.test_val, 9)
        self.assertEqual(tm3.test_val, 9)
        tm.delete()

    def test_unknown_names_raise_exception(self):
        """ Tests that passing in names for columns that don't exist raises an exception """
        tm = TestVertexModel.create(test_val=8, text='123456789')
        with self.assertRaises(TypeError):
            tm.update(jon='beard')
        tm.delete()


@attr('unit', 'vertex_io')
class TestVertexTraversal(BaseMogwaiTestCase):
    def setUp(self):
        super(TestVertexTraversal, self).setUp()
        self.v1 = TestVertexModel.create(test_val=1, name='Test1')
        self.v2 = TestVertexModel.create(test_val=2, name='Test2')
        self.v3 = OtherTestModel.create(test_val=3, name='Test3')
        self.v4 = OtherTestModel.create(test_val=3, name='Test3')

    def tearDown(self):
        self.v1.delete()
        self.v2.delete()
        self.v3.delete()
        self.v4.delete()

    def test_outgoing_vertex_traversal(self):
        """Test that outgoing vertex traversals work."""
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=12)
        e2 = TestEdgeModel.create(self.v1, self.v3, test_val=13)
        e3 = TestEdgeModel.create(self.v2, self.v3, test_val=14)

        results = self.v1.outV(TestEdgeModel)
        self.assertEqual(len(results), 2)
        self.assertIn(self.v2, results)
        self.assertIn(self.v3, results)

        results = self.v1.outV(TestEdgeModel, types=[OtherTestModel])
        self.assertEqual(len(results), 1)
        self.assertIn(self.v3, results)

        e1.delete()
        e2.delete()
        e3.delete()

    def test_incoming_vertex_traversal(self):
        """Test that incoming vertex traversals work."""
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=12)
        e2 = TestEdgeModel.create(self.v1, self.v3, test_val=13)
        e3 = TestEdgeModel.create(self.v2, self.v3, test_val=14)

        results = self.v2.inV(TestEdgeModel)
        self.assertEqual(len(results), 1)
        self.assertIn(self.v1, results)

        results = self.v2.inV(TestEdgeModel, types=[OtherTestModel])
        self.assertEqual(len(results), 0)

        e1.delete()
        e2.delete()
        e3.delete()

    def test_outgoing_edge_traversals(self):
        """Test that outgoing edge traversals work."""
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=12)
        e2 = TestEdgeModel.create(self.v1, self.v3, test_val=13)
        e3 = OtherTestEdge.create(self.v2, self.v3, test_val=14)

        results = self.v2.outE()
        self.assertEqual(len(results), 1)
        self.assertIn(e3, results)

        results = self.v2.outE(types=[TestEdgeModel])
        self.assertEqual(len(results), 0)

        e1.delete()
        e2.delete()
        e3.delete()

    def test_incoming_edge_traversals(self):
        """Test that incoming edge traversals work."""
        e1 = TestEdgeModel.create(self.v1, self.v2, test_val=12)
        e2 = TestEdgeModel.create(self.v1, self.v3, test_val=13)
        e3 = OtherTestEdge.create(self.v2, self.v3, test_val=14)

        results = self.v2.inE()
        self.assertEqual(len(results), 1)
        self.assertIn(e1, results)

        results = self.v2.inE(types=[OtherTestEdge])
        self.assertEqual(len(results), 0)

        e1.delete()
        e2.delete()
        e3.delete()

    def test_multiple_label_traversals(self):
        """ Tests that using multiple edges for traversals works """
        e1 = TestEdgeModel.create(self.v1, self.v2)
        e2 = OtherTestEdge.create(self.v1, self.v3)
        e3 = YetAnotherTestEdge.create(self.v1, self.v4)

        self.assertEqual(len(self.v1.outV()), 3)

        self.assertEqual(len(self.v1.outV(TestEdgeModel)), 1)
        self.assertEqual(len(self.v1.outV(OtherTestEdge)), 1)
        self.assertEqual(len(self.v1.outV(YetAnotherTestEdge)), 1)

        out = self.v1.outV(TestEdgeModel, OtherTestEdge)
        self.assertEqual(len(out), 2)
        self.assertIn(self.v2.id, [v.id for v in out])
        self.assertIn(self.v3.id, [v.id for v in out])

        out = self.v1.outV(OtherTestEdge, YetAnotherTestEdge)
        self.assertEqual(len(out), 2)
        self.assertIn(self.v3.id, [v.id for v in out])
        self.assertIn(self.v4.id, [v.id for v in out])

        e1.delete()
        e2.delete()
        e3.delete()

    def test_multiple_edge_traversal_with_type_filtering(self):
        """ Tests that using multiple edges for traversals works """
        v = TestVertexModel.create(test_val=1, name='Test1')

        v1 = TestVertexModel.create()
        e1 = TestEdgeModel.create(v, v1)

        v2 = TestVertexModel.create()
        e2 = OtherTestEdge.create(v, v2)

        v3 = TestVertexModel.create()
        e3 = YetAnotherTestEdge.create(v, v3)

        v4 = OtherTestModel.create()
        e4 = TestEdgeModel.create(v, v4)

        v5 = OtherTestModel.create()
        e5 = OtherTestEdge.create(v, v5)

        v6 = OtherTestModel.create()
        e6 = YetAnotherTestEdge.create(v, v6)

        self.assertEqual(len(v.outV()), 6)

        self.assertEqual(len(v.outV(TestEdgeModel, OtherTestEdge)), 4)
        self.assertEqual(len(v.outV(TestEdgeModel, OtherTestEdge, types=[TestVertexModel])), 2)

        e1.delete()
        e2.delete()
        e3.delete()
        e4.delete()
        e5.delete()
        e6.delete()
        v.delete()
        v1.delete()
        v2.delete()
        v3.delete()
        v4.delete()
        v5.delete()
        v6.delete()

    def test_edge_instance_traversal_types(self):
        """ Test traversals with edge instances work properly """
        te = TestEdgeModel.create(self.v1, self.v2)
        ote = OtherTestEdge.create(self.v1, self.v3)
        yate = YetAnotherTestEdge.create(self.v1, self.v4)

        out = self.v1.outV(te, ote)
        self.assertEqual(len(out), 2)
        self.assertIn(self.v2.id, [v.id for v in out])
        self.assertIn(self.v3.id, [v.id for v in out])

        out = self.v1.outV(ote, yate)
        self.assertEqual(len(out), 2)
        self.assertIn(self.v3.id, [v.id for v in out])
        self.assertIn(self.v4.id, [v.id for v in out])

        te.delete()
        ote.delete()
        yate.delete()

    def test_edge_label_string_traversal_types(self):
        """ Test traversals with edge instances work properly """
        e1 = TestEdgeModel.create(self.v1, self.v2)
        e2 = OtherTestEdge.create(self.v1, self.v3)
        e3 = YetAnotherTestEdge.create(self.v1, self.v4)

        out = self.v1.outV(TestEdgeModel.get_label(), OtherTestEdge.get_label())
        self.assertEqual(len(out), 2)
        self.assertIn(self.v2.id, [v.id for v in out])
        self.assertIn(self.v3.id, [v.id for v in out])

        out = self.v1.outV(OtherTestEdge.get_label(), YetAnotherTestEdge.get_label())
        self.assertEqual(len(out), 2)
        self.assertIn(self.v3.id, [v.id for v in out])
        self.assertIn(self.v4.id, [v.id for v in out])

        e1.delete()
        e2.delete()
        e3.delete()

    def test_unknown_edge_traversal_filter_type_fails(self):
        """
        Tests an exception is raised if a traversal filter is
        used that's not an edge class, instance or label string fails
        """
        e1 = TestEdgeModel.create(self.v1, self.v2)
        e2 = OtherTestEdge.create(self.v1, self.v3)
        e3 = YetAnotherTestEdge.create(self.v1, self.v4)

        with self.assertRaises(MogwaiException):
            out = self.v1.outV(5)

        with self.assertRaises(MogwaiException):
            out = self.v1.outV(True)

        e1.delete()
        e2.delete()
        e3.delete()

    @attr('manual_properties')
    def test_manual_properties(self):
        v = TestVertexModel.create(test_val=1, name='Test 7', some_property=32)

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
        v.save()
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

        v.delete()
