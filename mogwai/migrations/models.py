from mogwai.models import Vertex, Edge
from mogwai.properties import String, DateTime
from mogwai.relationships import Relationship
from mogwai.gremlin import GremlinMethod
import datetime
from pytz import utc
from functools import partial


class Migration(Vertex):
    element_type = 'mogwai_migration'
    package_name = String(max_length=255, required=True)
    migration_name = String(max_length=255, required=True)
    applied = DateTime(partial(datetime.datetime.now, tz=utc), required=True)

    _find_for_migration = GremlinMethod(method_name='find_for_migration', classmethod=True)

    @classmethod
    def for_package(cls, package_name):
        return cls.find_by_value('package_name', package_name)

    @classmethod
    def for_migration(cls, package, migration_name):
        try:
            return
        except cls.DoesNotExist:
            return cls.create(app_name=migration.app_label(),
                              migration=migration.name())

    def get_migrations(self):
        """ Get migrations (import from files)
        :return:
        """
        pass

    def get_migration(self):
        """ Get a single migration (import form file)

        :return:
        """
        pass

    def __repr__(self):
        return '{}(app_name={}, migration={}, applied={})'.format(
            self.__class__.__name__, self.app_name, self.migration, self.applied
        )


class PerformedMigration(Edge):

    label = 'performed_migration'


class MigrationDependency(Edge):

    label = 'migration_depends_on'
