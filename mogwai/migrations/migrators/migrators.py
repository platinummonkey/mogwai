from mogwai._compat import print_, string_types
from mogwai.exceptions import MogwaiMigrationException


class BaseMigration(object):

    models = {}
    complete_apps = []
    depends_on = ()

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

        db.execute(db._generate_script())


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

        with open(self.output_file, mode='wb') as f:
            f.writelines(db._generate_script())
