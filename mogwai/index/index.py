from __future__ import unicode_literals
from base import BaseIndexSpecification
from functools import partial


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
    _compiled_composite_index = ''
    _deferred_commands = []
    var_assignment = False

    #TODO: finish these

    def _get_index_variable_name(self, model):
        return "{}_{}".format(model.get_label(), self.index_key)

    def _add_property_key(self, key, model):
        """ Add a property key

        :param key: property name
        :param model: mogwai.models.Vertex | mogwai.models.Edge
        """
        if key in model._properties:
            if model._properties[key].index:
                index_key = model._properties[key].index_key
            else:
                index_key = model._properties[key].db_field_name
        else:
            index_key = key

        self._compiled_composite_index = self._compiled_composite_index + '.addKey(mgmt.getPropertyKey("{}"))'.format(
            index_key
        )

    def add_property_key(self, key):
        self._composite_index.append(partial(self._add_property_key(key=key)))

    def _make_unique(self):
        self._compiled_composite_index += '.unique()'

    def _set_consistency(self, consistency):
        self._deferred_commands.append('mgmt.setConsistency(mgmt.getGraphIndex("{}"), {})'.format(
            self.index_key, consistency
        ))

    def _build_vertex_centric_index(self):
        self._compiled_composite_index = self._compiled_composite_index + '.buildIndex("{}", Vertex.class'.format(
            self.index_key
        )

    def _build_mixed_index(self):
        if self.index_ext:
            index_ext = '"{}"'.format(self.index_ext)
        else:
            index_ext = ''
        self._compiled_composite_index = self._compiled_composite_index + ".buildMixedIndex({})".format(index_ext)

    def _build_composite_index(self):
        self._compiled_composite_index += '.buildCompositeIndex()'

    def _wait_until_index_registered(self):
        self._deferred_commands.append("""// Block until the SchemaStatus transitions from INSTALLED to REGISTERED
registered = false
before = System.currentTimeMillis()
while (!registered) {
    Thread.sleep(500L)
    mgmt = g.getManagementSystem()
    idx  = mgmt.getGraphIndex("{}")
    registered = true
    for (k in idx.getFieldKeys()) {
        s = idx.getIndexStatus(k)
        registered &= s.equals(SchemaStatus.REGISTERED)
    }
    mgmt.rollback()
}""".format(self._get_index_variable_name()))

    def _deferred_update_index(self):
        self._deferred_commands.append(
            'mgmt.updateIndex(mgmt.getGraphIndex("{}"), SchemaAction.ENABLE_INDEX);'.format(
                self._get_index_variable_name()
            )
        )

    def generate(self):
        return ''

    def generate_deferred(self):
        return ''

    def generate_deferred_delete(self):
        return ''