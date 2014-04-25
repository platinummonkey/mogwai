from __future__ import unicode_literals
from nose.plugins.attrib import attr

from mogwai.tests.base import BaseMogwaiTestCase, TestVertexModel, TestEdgeModel
from mogwai.exceptions import ModelException, MogwaiException, ValidationError
from mogwai.models import Vertex, Edge
from mogwai import properties


class WildDBNames(Vertex):
    name = properties.String(db_field="words_and_whatnot")
    test_val = properties.Integer(db_field="integers_etc")


@attr('unit', 'class_construction')
class TestModelClassFunction(BaseMogwaiTestCase):
    """
    Tests verifying the behavior of the Model metaclass
    """

    def test_graph_property_attributes_handled_correctly(self):
        """
        Tests that graph property attributes are moved to a _properties dict and replaced with simple value attributes
        """

        #check class attributes
        self.assertHasAttr(TestVertexModel, '_properties')
        self.assertHasAttr(TestVertexModel, 'name')
        self.assertHasAttr(TestVertexModel, 'test_val')

        #check instance attributes
        inst = TestVertexModel()
        self.assertHasAttr(inst, 'name')
        self.assertHasAttr(inst, 'test_val')
        self.assertIsNone(inst.name)
        self.assertIsNone(inst.test_val)

    def test_db_map(self):
        """
        Tests that the db_map is properly defined

        The db_map allows graph properties to be named something other than their variable name
        """

        db_map = WildDBNames._db_map
        self.assertIn('wilddbnames_words_and_whatnot', db_map)
        self.assertIn('wilddbnames_integers_etc', db_map)
        self.assertEquals(db_map['wilddbnames_words_and_whatnot'], 'name')
        self.assertEquals(db_map['wilddbnames_integers_etc'], 'test_val')

    def test_attempting_to_make_duplicate_column_names_fails(self):
        """
        Tests that trying to create conflicting db column names will fail
        """

        with self.assertRaises(ModelException):
            class BadNames(Vertex):
                words = properties.Text()
                content = properties.Text(db_field='words')

    def test_value_managers_are_keeping_model_instances_isolated(self):
        """
        Tests that instance value managers are isolated from other instances
        """
        inst1 = TestVertexModel(test_val=5)
        inst2 = TestVertexModel(test_val=7)

        self.assertNotEquals(inst1.test_val, inst2.test_val)
        self.assertEquals(inst1.test_val, 5)
        self.assertEquals(inst2.test_val, 7)


@attr('unit', 'class_construction')
class TestManualTableNaming(BaseMogwaiTestCase):

    def test_proper_table_naming(self):
        self.assertEqual(TestVertexModel.element_type, 'test_vertex_model')
        self.assertEqual(TestVertexModel.get_element_type(), 'test_vertex_model')


class BaseAbstractVertex(Vertex):
    __abstract__ = True
    data = properties.Text()


class DerivedAbstractVertex(BaseAbstractVertex):
    pass


@attr('unit', 'class_construction')
class TestAbstractElementAttribute(BaseMogwaiTestCase):

    def test_abstract_property_is_not_inherited(self):
        self.assertTrue(BaseAbstractVertex.__abstract__)
        self.assertFalse(DerivedAbstractVertex.__abstract__)

    def test_abstract_element_persistence_methods_fail(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bm = BaseAbstractVertex(data='something')

            with self.assertRaises(MogwaiException):
                bm.save()

            with self.assertRaises(MogwaiException):
                bm.delete()

            with self.assertRaises(MogwaiException):
                bm.update(data='something else')