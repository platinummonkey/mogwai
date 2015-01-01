from mogwai._compat import string_types
from mogwai.exceptions import MogwaiMigrationException
from mogwai.tools import import_string, ImportStringError
from mogwai._compat import print_
from mogwai.connection import Configuration


def get_import_path_for_class(klass):
    return klass.__module__ + '.' + klass.__name__


def get_loaded_models():
    """ Get all loaded models

    :return: list of all loaded models
    :rtype: [Element]
    """
    return [model for model in Configuration._get_loaded_models()
            if (not model.__abstract__ and model.__name__ not in ('Element', 'Vertex', 'Edge'))]


def get_loaded_models_for_app(app):
    """ Only return loaded models that match a given app name

    ie. given:
        myapp
          models.py
            - MyVertex
        myotherapp
          models.py
            -MyOtherVertex

    assert get_loaded_models_for_app('myapp.models') == '[MyVertex]'

    :param app: application name
    :type app: basestring
    :return: list of loaded models matching app location
    :rtype: [Element]
    """
    all_models = get_loaded_models()
    return [model for model in all_models if '.'.join(model.__module__.split('.')[:-1]) == app]


def ask_for_it_by_name(name):
    """ Returns an object referenced by absolute path. (Memoised outer wrapper)

    :param name: string reference to import
    :return: mogwai.models.element.Element | mogwai.models.properties.base.GraphProperty
    """
    if name not in ask_for_it_by_name.cache:
        try:
            ask_for_it_by_name.cache[name] = import_string(name)
        except ImportStringError as e:
            raise MogwaiMigrationException(e.message)
    return ask_for_it_by_name.cache[name]
ask_for_it_by_name.cache = {}


class BaseMigration(object):

    models = {}
    complete_apps = []
    depends_on = ()

    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def forwards(self, db):  # pragma: no cover
        raise NotImplementedError("Must override BaseMigration class")

    def backwards(self, db):  # pragma: no cover
        raise NotImplementedError("Must override BaseMigration class")

    def execute(self, db, forwards=True):  # pragma: no cover
        if forwards:
            self.forwards(db)
        else:
            self.backwards(db)


class SchemaMigration(BaseMigration):

    def execute(self, db, forwards=True):
        """ Writes the generated migration script to a file

        :param db: database operation instance
        :type db: mogwai.migrations.operation.DatabaseOperation
        """
        super(SchemaMigration, self).execute(db, forwards=forwards)

        if not self.dry_run:
            db.execute(db._generate_script())
        else:  # pragma: no cover
            output = '-'*80
            output = output + '\nMigration for {} to be executed\n'.format(self.complete_apps)
            output = output + '{}\n'.format(db._generate_script()) + '-'*80
            print_(output)


class SchemaFileGeneratorMigration(BaseMigration):

    output_file = ''

    def execute(self, db, forwards=True):
        """ Writes the generated migration script to a file

        :param db: database operation instance
        :type db: mogwai.migrations.operation.DatabaseOperation
        """
        super(SchemaFileGeneratorMigration, self).execute(db, forwards=forwards)

        if self.output_file in ('', None) or not isinstance(self.output_file, string_types):
            raise MogwaiMigrationException("Output file must be a valid path string")

        if not self.dry_run:
            with open(self.output_file, mode='wb') as f:
                f.writelines(db._generate_script())
        else:  # pragma: no cover
            output = '-'*80
            output = output + '\nMigration for {} to be written to {}\n'.format(self.complete_apps, self.output_file)
            output = output + '{}\n'.format(db._generate_script()) + '-'*80
            print_(output)
