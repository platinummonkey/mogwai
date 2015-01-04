from mogwai.models import Vertex, Edge, OUT, IN
from mogwai.properties import String, DateTime, UUID
from mogwai.relationships import Relationship
from mogwai.gremlin import GremlinMethod
import datetime
from pytz import utc
from functools import partial
from uuid import uuid4


class MigrationDependency(Edge):

    label = 'migration_depends_on'


class Migration(Vertex):
    element_type = 'mogwai_migration'
    uuid = UUID(required=True)
    package_name = String(max_length=255, required=True)
    migration_name = String(max_length=255, required=True)
    applied = DateTime(partial(datetime.datetime.now, tz=utc), required=True)

    _find_for_migration = GremlinMethod(method_name='find_for_migration', classmethod=True)
    depends_on = Relationship(MigrationDependency, 'mogwai.migrations.models.Migration', direction=OUT)
    required_for = Relationship(MigrationDependency, 'mogwai.migrations.models.Migration', direction=IN)

    @classmethod
    def generate_migration_id(cls):
        return str(uuid4())

    @classmethod
    def for_uuid(cls, uuid):
        return cls.find_by_value('uuid', uuid)

    @classmethod
    def for_package(cls, package_name):
        return cls.find_by_value('package_name', package_name)

    @classmethod
    def for_migration(cls, package, migration_name):
        try:
            return
        except cls.DoesNotExist:
            return cls.create(package_name=package.package_label,
                              migration_name=migration_name)

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
        return '{}(uuid={}, package_name={}, migration_name={}, applied={})'.format(
            self.__class__.__name__, self.uuid, self.package_name, self.migration_name, self.applied
        )
