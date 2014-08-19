from __future__ import unicode_literals
import datetime
from mogwai.migrations import db, SchemaMigration
from mogwai.connection import _loaded_models


class Migration(SchemaMigration):

    # depends on this any other migration files?
    depends_on = (
        #("otherapp", "0001_initial"),
    )

    def forwards(self, ogm):
        # Adding property 'phone' to 'Person'
        db.add_property(
            'person', 'person_phone',
            self.gf('mogwai.properties.String')(required=False, max_length=15, default=None),
            keep_default=False,
        )

    def backwards(self, ogm):

        # Delete property 'phone' from 'Person'
        db.delete_property(
            'person', 'person_phone'
        )

    models = {
        'models.Trinket': {
            '__type': 'vertex',
            'name': ('mogwai.properties.String', [], {'required': 'True', 'max_length': '1024'})
        },
        'models.Person': {
            '__type': 'vertex',
            'name': ('mogwai.properties.String', [], {'required': 'True', 'max_length': '512'}),
            'email': ('mogwai.properties.Email', [], {'required': 'True'}),
            'phone': ('mogwai.properties.String', [], {'required': 'False', 'max_length': '15'})
        },
        'models.OwnsObject': {
            '_type': 'edge',
            'since': ('mogwai.properties.DateTime', [], {'required': 'True'})
        }
    }

    complete_apps = ['models']
