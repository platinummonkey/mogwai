from __future__ import unicode_literals
from mogwai.migrations.migrators import SchemaMigration


class Migration(SchemaMigration):

    # depends on this any other migration files?
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
