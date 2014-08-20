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
    def for_migration(cls, migration):
        try:
            return cls.find_by_value(cls.migration, migration)
        except cls.DoesNotExist:
            return cls.create(app_name=migration.app_label(),
                              migration=migration.name())