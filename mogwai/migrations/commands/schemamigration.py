from __future__ import unicode_literals
from base import BaseCommand
import os
from string import Template
from mogwai._compat import print_
from mogwai.migrations.models import Migration, MigrationDependency


class SchemaMigrationCommand(BaseCommand):

    def setup_args(self):
        super(SchemaMigrationCommand, self).setup_args()
        # --app - Specify the app
        # --initial - Generate the initial schema for the app, store_true, initial
        # --empty - Generate a blank migration, store_true, empty
        # --auto - Attempt to automatically detect differences in the last migration
        # --update - Attempt to update the previously created migration - Overwrites!
        # default parameters
        self.parser.add_argument('-p', '--package', type=str, help='Specify the package')
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('--initial', action='store_true', help='Generate the initial schema for the app')
        group.parser.add_argument('--empty', action='store_true', help='Generate a blank migration')
        group.parser.add_argument('--auto', action='store_true',
                                  help='Attempt to automatically detect differences in the last migration')
        group.parser.add_argument('--update', action='store_true',
                                  help='Attempt to update the previously created migration. Beware this overwrites!')

    def check_output_path(self, filename, filepath=None):
        if filepath is None:
            if self.args.package in ('', '.', None):
                self.args.package = ''
            mpath = os.path.join(os.path.abspath(self.args.package.replace('.', '/')), 'migrations')
            if not os.path.exists(mpath):
                os.mkdir(mpath)
            init_file = os.path.join(mpath, '__init__.py')
            if not os.path.exists(init_file):
                open(init_file, 'w').close()  # touch the file
            return os.path.join(mpath, filename)
        else:
            if filepath in ('', './', '.'):
                filepath = ''
            filepath = os.path.abspath(filepath)
            if not os.path.exists(filepath):
                os.mkdir(filepath)
            init_file = os.path.join(filepath, '__init__.py')
            if not os.path.exists(init_file):
                open(init_file, 'w').close()  # touch the file
            return os.path.join(filepath, filename)

    def handle(self, package=None, initial=False, empty=False, auto=True, dry_run=False, *args, **kwargs):
        uuid = Migration.generate_migration_id()
        if empty:
            filename = self.check_output_path(filename='blank_migration.py')
            with open(filename, 'wb') as f:
                f.write(Template(MIGRATION_TEMPLATE).safe_substitute(
                    forwards='        raise NotImplementedError("This needs to be replaced")',
                    backwards='        raise NotImplementedError("This needs to be replaced")',
                    frozen_models={}, uuid=uuid, depends_on=[]
                ))
            print_("Wrote blank migration file to {}".format(filename))
            return

        if initial:
            return

        if auto:
            if dry_run:
                #output = '-'*80
                #output = output + '\nMigration for {} to be executed\n'.format(self.complete_apps)
                #output = output + '{}\n'.format(db._generate_script()) + '-'*80
                #print_(output)
                pass
            return

        # TODO: future - support manual additions like South

    def forwards_code(self):
        return ''

    def backwards_code(self):
        return ''


MIGRATION_TEMPLATE = '''# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mogwai.migrations.operation import DatabaseOperation
from mogwai.migrations.migrators import SchemaMigration
from mogwai.migrations.state import MockVertex as Vertex, MockEdge as Edge

class Migration(SchemaMigration):

   uuid = '$uuid'

   def forwards(self, db):
$forwards

   def backwards(self, db):
$backwards

   models = $frozen_models

   depends_on = $depends_on

'''


if __name__ == '__main__':
    c = SchemaMigrationCommand()
    c()