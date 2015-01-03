from __future__ import unicode_literals
from nose.plugins.attrib import attr
from mogwai.tests.base import BaseMogwaiTestCase
from mogwai.migrations.migrators import SchemaMigration
from mogwai.migrations.migrations.migration_file import *
from mogwai.properties import String


class Migration(SchemaMigration):

    depends_on = ()

    def forwards(self, db):
        pass

    def backwards(self, db):
        pass

    models = {
        'models.Trinket': {
            'type': 'vertex',
            'label': 'trinket',
            'properties': {
                'name': ('mogwai.properties.String', 'trinket_name', {'required': 'True', 'max_length': '1024'})
            },
            'composite_indices': {}
        },
        'models.Person': {
            'type': 'vertex',
            'label': 'person',
            'properties': {
                'name': ('mogwai.properties.String', 'person_name', {'required': 'True', 'max_length': '512'}),
                'email': ('mogwai.properties.Email', 'person_email', {'required': 'True'})
            },
            'composite_indices': {}
        },
        'models.OwnsObject': {
            'type': 'edge',
            'label': 'owns',
            'properties': {
                'since': ('mogwai.properties.DateTime', 'owns_since', {'required': 'True'})
            },
            'composite_indices': {}
        }
    }


@attr('unit', 'migration_tests', 'migration_tests_migration_file')
class TestMigrationFile(BaseMogwaiTestCase):
    """ Test the MigrationFile processing """

    def test_migration_file_instantiation(self):
        mf = MigrationFile(index=0, filename='0001_initial.py', migration_klass=Migration, package_migrations=None)

    def test_migration_file_get_stripped_filename(self):
        mf = MigrationFile(index=0, filename='0001_initial.py', migration_klass=Migration, package_migrations=None)
        self.assertEqual('0001_initial', mf.stripped_filename)

    def test_migration_file_regenerate_models(self):
        mf = MigrationFile(index=0, filename='0001_initial.py', migration_klass=Migration, package_migrations=None)
        mf.regenerate_models()
        self.assertEqual(3, len(mf.models_by_ref))
        self.assertEqual(3, len(mf.models_by_label))
        self.assertTrue('trinket' in mf.models_by_label)
        self.assertTrue('models.Trinket' in mf.models_by_ref)
        self.assertIsInstance(mf.models_by_label['trinket'], MockVertex)
        trinket = mf.models_by_label['trinket']
        self.assertEqual(trinket, mf.get_model_by_label('trinket'))
        self.assertEqual(trinket, mf.get_model_by_ref('models.Trinket'))
        self.assertEqual(1, len(trinket._properties))
        self.assertIsInstance(trinket._properties.items()[0][1], String)
        self.assertEqual(trinket._properties.items()[0][1],
                         mf.models_by_ref['models.Trinket']._properties.items()[0][1])
        self.assertTrue(trinket._properties.items()[0][1].required)
