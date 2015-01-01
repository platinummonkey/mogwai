from mogwai.exceptions import MogwaiMigrationException
from mogwai.tools import import_string, ImportStringError
from mogwai._compat import print_
from mogwai.connection import Configuration


def get_loaded_models():
    return [model for model in Configuration.__loaded_models
            if (not model.__abstract__ and model.__name__ not in ('Element', 'Vertex', 'Edge'))]


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

    def execute(self, db):  # pragma: no cover
        raise NotImplementedError("Must override BaseMigration class")


class SchemaMigration(BaseMigration):
    pass


class SchemaFileGeneratorMigration(BaseMigration):

    output_file = ''

    def execute(self, db):
        """ Writes the generated migration script to a file

        :param db: database operation instance
        :type db: mogwai.migrations.operation.DatabaseOperation
        """
        if not self.dry_run:
            with open(self.output_file, mode='wb') as f:
                f.writelines(db._generate_script())
        else:  # pragma: no cover
            output = '-'*80
            output = output + '\nMigration for {} to be written to {}\n'.format(self.complete_apps, self.output_file)
            output = output + '{}\n'.format(db._generate_script()) + '-'*80
            print_(output)
