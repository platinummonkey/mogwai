from __future__ import unicode_literals


class MogwaiException(Exception):
    """ Generic Base Exception for Mogwai Library """
    pass


class MogwaiConnectionError(MogwaiException):
    """ Problem connecting with Titan """
    pass


class MogwaiGraphMissingError(MogwaiException):
    """ Graph with specified name does not exist """
    pass


class MogwaiQueryError(MogwaiException):
    """ Exception thrown when a query error occurs """
    pass


class ValidationError(MogwaiException):
    """ Exception thrown when a property value validation error occurs """

    def __init__(self, *args, **kwargs):
        self.code = kwargs.pop('code', None)
        super(MogwaiException, self).__init__(*args, **kwargs)


class ElementDefinitionException(MogwaiException):
    """ Error in element definition """
    pass


class ModelException(MogwaiException):
    """ Error in model """
    pass


class SaveStrategyException(MogwaiException):
    """ Exception thrown when a Save Strategy error occurs """
    pass


class MogwaiGremlinException(MogwaiException):
    """ Exception thrown when a Gremlin error occurs """
    pass


class MogwaiRelationshipException(MogwaiException):
    """ Exception thrown when a Relationship error occurs """
    pass


class MogwaiMetricsException(MogwaiException):
    """ Exception thrown when a metric system error occurs """
    pass
