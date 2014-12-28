from os import environ

# in blueprints this is part of the Query.compare
# see http://www.tinkerpop.com/docs/javadocs/blueprints/2.2.0/
EQUAL = "EQUAL"
GREATER_THAN = "GREATER_THAN"
GREATER_THAN_EQUAL = "GREATER_THAN_EQUAL"
LESS_THAN = "LESS_THAN"
LESS_THAN_EQUAL = "LESS_THAN_EQUAL"
NOT_EQUAL = "NOT_EQUAL"

# direction
OUT = "OUT"
IN = "IN"
BOTH = "BOTH"


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class Configuration(object):

    class DeleteMethods(object):
        REMOVE_ON_DELETE = 'REMOVE'
        FLAG_FOR_DELETE = 'FLAG'

    class BackendDatabases(object):
        CASSANDRA = 'cassandra'
        HADOOP2 = 'hbase'
        HADOOP1 = 'hbase'
        BERKELEY = None

    delete_method = DeleteMethods.REMOVE_ON_DELETE  # currently unused
    backend_database = BackendDatabases.CASSANDRA  # used to determine the method for index job repair
    __database_properties_file = None

    @property
    def database_properties_file(self):
        if self.__database_properties_file is None:
            return environ.get('TITAN_PROPERTIES_FILE', 'titan-{}-es.properties'.format(self.backend_database.lower()))
        else:
            return environ.get('TITAN_PROPERTIES_FILE', self.__database_properties_file)

    @classmethod
    def set_database_properties_file(cls, filename):
        cls.__database_properties_file = filename


__all__ = ['EQUAL', 'GREATER_THAN', 'GREATER_THAN_EQUAL', 'LESS_THAN', 'LESS_THAN_EQUAL', 'NOT_EQUAL', 'OUT', 'IN',
           'BOTH', 'Configuration']