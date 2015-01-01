from __future__ import unicode_literals
from base import BaseCommand


class SchemaMirationCommand(BaseCommand):

    def setup_args(self):
        # --app - Specify the app
        # --initial - Generate the initial schema for the app, store_true, initial
        # --empty - Generate a blank migration, store_true, empty
        # --auto - Attempt to automatically detect differences in the last migration
        self.parser.add_argument()

    def forwards_code(self):
        return ''

    def backwards_code(self):
        return ''


MIGRATION_TEMPLATE = '''# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mogwai.migrations.operation import DatabaseOperation
from mogwai.migrations.utils import SchemaMigration
from mogwai.migrations.state import MockVertex as Vertex, MockEdge as Edge

class Migration(SchemaMigration):

   def forwards(self, db):
$forwards

   def backwards(self, db):
$backwards

   models = $frozen_models

   complete_apps = $complete_apps


'''


if __name__ == '__main__':
    c = SchemaMirationCommand()
    c()