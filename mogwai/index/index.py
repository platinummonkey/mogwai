from base import BaseIndexSpecification


class PropertyIndex(BaseIndexSpecification):
    """ Property Index Specification """

    def __init__(self, partition=False, cardinality=None, ttl=None, immutable=False, **kwargs):
        self.partition = partition
        self.cardinality = cardinality
        self.ttl = ttl
        self.immutable = immutable
        super(PropertyIndex, self).__init__(**kwargs)


class LabelIndex(BaseIndexSpecification):
    """ Vertex or Edge Label Index Specification """

    def __init__(self, label=None, **kwargs):
        self.label = label
        super(LabelIndex, self).__init__(**kwargs)


class CompositeIndex(BaseIndexSpecification):
    """ A composite index composing of additional indices or parameters """

    _composite_index = []

    #TODO: finish these

    def get_specification(self):
        pass
