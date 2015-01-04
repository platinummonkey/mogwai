from __future__ import unicode_literals
from mogwai.migrations.migrators import SchemaMigration


class Migration(SchemaMigration):

    uuid = '1a4cfb03-12af-4bf1-944f-cad83177c2bf'

    # depends on this any other migration files?
    depends_on = (
        # FUTURE: ("otherapp", "0001_initial"),
        # CURRENT:
        '0001_initial'
    )

    def forwards(self, db):
        # Adding property 'phone' to 'Person'
        db.add_property(
            'person', 'person_phone',
            self.gf('mogwai.properties.String')(required=False, max_length=15, default=None),
            keep_default=False,
        )

    def backwards(self, db):

        # Delete property 'phone' from 'Person'
        db.delete_property(
            'person', 'person_phone'
        )

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

