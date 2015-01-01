from __future__ import unicode_literals
import datetime
from mogwai.migrations import db, SchemaMigration
from mogwai.connection import _loaded_models


class Migration(SchemaMigration):

    # depends on this any other migration files?
    depends_on = (
        #("otherapp", "0001_initial"),
    )

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
            '__type': 'vertex',
            'properties': {
                'name': ('mogwai.properties.String', [], {'required': 'True', 'max_length': '1024'})
            },
            'composite_indices': {}
        },
        'models.Person': {
            '__type': 'vertex',
            'properties': {
                'name': ('mogwai.properties.String', [], {'required': 'True', 'max_length': '512'}),
                'email': ('mogwai.properties.Email', [], {'required': 'True'})
            },
            'composite_indices': {}
        },
        'models.OwnsObject': {
            '_type': 'edge',
            'properties': {
                'since': ('mogwai.properties.DateTime', [], {'required': 'True'})
            },
            'composite_indices': {}
        }
    }

    complete_apps = ['models']
