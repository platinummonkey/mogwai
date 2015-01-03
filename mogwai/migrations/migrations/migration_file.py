from __future__ import unicode_literals
import warnings
import os
import re
from collections import OrderedDict
from utils import get_filepath_for_module, get_files_for_path
from mogwai.tools import import_string
from state import MockEdge, MockVertex
from mogwai.exceptions import MogwaiMigrationException


MIGRATION_FILE_PATTERN = re.compile(r'(?!__init__)'   # Don't match __init__.py
                                    r'[0-9a-zA-Z_]*'  # Don't match dotfiles, or names with dots/invalid chars in them
                                    r'(\.pyc?)?$')    # Match .py or .pyc files, or module dirs


class MigrationsSuite(object):
    """ FUTURE: Preloads all the individual package's migrations """
    pass


class PackageMigrations(object):
    """ A single package's migrations

    Identifies and orders dependencies
    """

    def __init__(self, module):
        self.module = module
        self.migrations = OrderedDict()
        self.get_migrations()

    def get_migrations(self):
        dirname = get_filepath_for_module(self.module)
        filenames = get_files_for_path(dirname, MIGRATION_FILE_PATTERN)
        for i, filename in enumerate(filenames):
            fm = os.path.splitext(os.path.basename(filename))[0]
            migration_name = '{}.{}.Migration'.format(self.module, fm)
            self.migrations[fm] = MigrationFile(i, filename, import_string(migration_name), self.migrations)
        self.resolve_dependencies()

    def resolve_dependencies(self):
        for migration in self.migrations:
            for dependency in migration.dependencies:
                if dependency in self.migrations:
                    self.migrations[dependency].dependents.add(migration.stripped_filename)
                else:
                    warnings.warn("Outside module dependencies are not currently supported!")
                    migration.dependencies.discard(dependency)

    def get_latest(self, update=False):
        if update:
            return self.migrations.items()[-2]
        return self.migrations.items()[-1]


class MigrationFile(object):
    """ Class which represents a particular migration file on-disk. """

    def __init__(self, index, filename, migration_klass, package_migrations):
        """

        :param filename: filename for the migration
        :type filename: str
        :param migration_klass: Migration imported from the given file
        :type migration_klass: mogwai.migrations.migrators.BaseMigration
        :param package_migrations: weak reference to the PackageMigrations
        :type package_migrations: PackageMigrations
        """
        self.index = index
        self.filename = filename
        self.migration = migration_klass()
        """ :type migration: mogwai.migrations.migrators.BaseMigration """
        self.dependencies = set()
        self.dependents = set()
        self.package_migrations = package_migrations
        self.models_by_ref = OrderedDict()
        self.models_by_label = OrderedDict()

    def __repr__(self):
        return '{}(filename={}, dependencies={}, dependents={})'.format(
            self.__class__.__name__, self.filename, self.dependencies, self.dependents
        )

    @property
    def stripped_filename(self):
        return os.path.splitext(os.path.basename(self.filename))[0]

    def regenerate_models(self):
        for model_ref, model_def in self.migration.models.items():
            element_type = model_def.get('type')
            label = model_def.get('label')
            properties = OrderedDict()
            for prop_name, prop_def in model_def.get('properties', {}).items():
                prop_klass = import_string(prop_def[0])
                properties[prop_name] = prop_klass(**prop_def[2])
                properties[prop_name].set_property_name(prop_def[1])
                if not properties[prop_name].has_db_field_prefix:
                    properties[prop_name].set_db_field_prefix(label)

            composite_indices = model_def.get('composite_indices', {})
            if element_type.lower() == 'vertex':
                model = MockVertex(label=label, props=properties, composite_indices=composite_indices)
            elif element_type.lower() == 'edge':
                model = MockEdge(label=label, props=properties, composite_indices=composite_indices)
            else:
                raise MogwaiMigrationException("Invalid Element Type: {}! Must be 'edge' or 'vertex'".format(
                    element_type)
                )

            self.models_by_ref[model_ref] = self.models_by_label[label] = model

    def get_previous(self):
        if self.index > 0:
            return self.package_migrations.migrations.items()[self.index-1]
        return None

    def get_model_by_ref(self, ref):
        return self.models_by_ref[ref]

    def get_model_by_label(self, label):
        return self.models_by_label[label]

    #def get_database_record_for_migration(self):
    #    record_uid = "{}.{}".format(self.package_migrations.module, )