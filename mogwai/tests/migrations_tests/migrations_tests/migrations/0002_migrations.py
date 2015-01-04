from __future__ import unicode_literals
from mogwai.migrations.migrators import SchemaMigration


class Migration(SchemaMigration):

    uuid = '8e7ce1f8-5796-4b2b-8a17-a020acea417a'

    # depends on this any other migration files?
    depends_on = (
        '0001_initial'
    )

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
                'email': ('mogwai.properties.Email', 'person_email', {'required': 'True'}),
                'phone': ('mogwai.properties.String', 'person_phone', {'required': 'False', 'max_length': '15'})
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

