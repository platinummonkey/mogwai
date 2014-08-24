from mogwai.models import Vertex
from mogwai.properties import String, DateTime
import datetime
from pytz import utc
from functools import partial


class MigrationHistory(Vertex):
    app_name = String(max_length=255)
    migration = String(max_length=255)
    applied = DateTime(partial(datetime.datetime.now, tz=utc))

    @classmethod
    def for_app(cls, app_name):
        return cls.find_by_value('app_name', app_name)

    @classmethod
    def for_migration(cls, migration):
        try:
            return cls.find_by_value('migration', migration)
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

    def __repr__(self):
        return '{}(app_name={}, migration={}, applied={})'.format(
            self.__class__.__name__, self.app_name, self.migration, self.applied
        )