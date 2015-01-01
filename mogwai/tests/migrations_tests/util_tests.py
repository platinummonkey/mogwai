from __future__ import unicode_literals

from nose.plugins.attrib import attr

from mogwai.tests.base import BaseMogwaiTestCase, TestVertexModel, TestEdgeModel
from mogwai.models import Vertex, Edge
from mogwai.models.element import Element
from mogwai.migrations.migrations.utils import get_loaded_models
from mogwai.tests.models.class_construction_tests import BaseAbstractVertex


@attr('unit', 'migration_tests', 'migration_tests_utils')
class TestMigrationUtils(BaseMogwaiTestCase):
    """ Test the utils module in migrations """

    def test_loaded_models(self):
        loaded_models = get_loaded_models()
        # Built-in abstract models should not be included
        self.assertNotIn(Vertex, loaded_models)
        self.assertNotIn(Edge, loaded_models)
        self.assertNotIn(Element, loaded_models)

        # User defined abstract model should not be included
        self.assertNotIn(BaseAbstractVertex, loaded_models)

        # User defined models that should be included
        self.assertIn(TestVertexModel, loaded_models)
        self.assertIn(TestEdgeModel, loaded_models)