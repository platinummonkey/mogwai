from __future__ import unicode_literals
from mogwai.migrations.migrators import SchemaMigration


class Migration(SchemaMigration):

    # depends on this any other migration files?
    depends_on = ()

    def forwards(self, db):
        # Adding Vertex Model 'Person'
        db.create_vertex_type(
            'person', (
                ('person_name', self.gf('mogwai.properties.String')(required=True, max_length=512)),
                ('person_email', self.gf('mogwai.properties.Email')(required=True))
            )
        )
        db.send_create_signal('vertex', 'person')

        # Adding Vertex Model Trinket
        db.create_vertex_type(
            'trinket', (
                ('trinket_name', self.gf('mogwai.properties.String')(required=True, max_length=1024))
            )
        )
        db.send_create_signal('vertex', 'trinket')

        # Adding Edge Model
        db.create_edge_type(
            'owns_object', (
                ('ownsobject_since', self.gf('mogwai.properties.DateTime')(required=True))
            )
        )
        db.send_create_signal('edge', 'owns_object')

    def backwards(self, db):

        # Deleting Edge model OwnsObject
        db.delete_edge_type('owns_object')

        # Deleting Vertex model Trinket
        db.delete_vertex_type('trinket')

        # Deleting Vertex model Person
        db.delete_vertex_type('person')

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
