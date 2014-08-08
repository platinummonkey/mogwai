from __future__ import unicode_literals
from collections import OrderedDict
import re

from mogwai._compat import string_types, print_, add_metaclass
from mogwai.tools import import_string
from mogwai import properties
from mogwai.exceptions import MogwaiException, SaveStrategyException, \
    ModelException, ElementDefinitionException
from mogwai.gremlin import BaseGremlinMethod
from mogwai.connection import _add_model_to_space

# import for backward compatibility
from mogwai.constants import BOTH, EQUAL, GREATER_THAN, GREATER_THAN_EQUAL, \
    IN, LESS_THAN, LESS_THAN_EQUAL, NOT_EQUAL, OUT


import logging
import warnings
logger = logging.getLogger(__name__)

#dict of node and edge types for rehydrating results
vertex_types = {}
edge_types = {}


class BaseElement(object):
    """
    The base model class, don't inherit from this, inherit from Model, defined
    below
    """
    #__enum_id_only__ = True
    FACTORY_CLASS = None

    class DoesNotExist(MogwaiException):
        """
        Object not found in database
        """
        pass

    class MultipleObjectsReturned(MogwaiException):
        """
        Multiple objects returned on unique key lookup
        """
        pass

    class WrongElementType(MogwaiException):
        """
        Unique lookup with key corresponding to vertex of different type
        """
        pass

    def __init__(self, **values):
        """
        Initialize the element with the given properties.

        :param values: The properties for this element
        :type values: dict

        """
        self._id = values.get('_id')
        self._values = {}
        self._manual_values = {}
        #print_("Received values: %s" % values)
        #print_("Known Relationships: %s" % self._relationships)
        for name, prop in self._properties.items():
            #print_("trying name: %s in values" % name)
            value = values.get(name, None)
            if value is not None:
                #print_("Got value")
                value = prop.to_python(value)
            #else:
                #print_("no value found")
            value_mngr = prop.value_manager(prop, value, prop.save_strategy)
            self._values[name] = value_mngr
            setattr(self, name, value)
        for name, relationship in self._relationships.items():
            relationship._setup_instantiated_vertex(self)

        # unknown properties that are loaded manually
        from mogwai.properties.base import BaseValueManager
        for kwarg in set(values.keys()).difference(set(self._properties.keys())):  # set(self._properties.keys()) - set(values.keys()):
            if kwarg not in ('_id', '_inV', '_outV', 'element_type'):
                self._manual_values[kwarg] = BaseValueManager(None, values.get(kwarg))

    @property
    def id(self):
        return self._id

    def __eq__(self, other):
        """
        Check for equality between two elements.

        :param other: Element to be compared to
        :type other: BaseElement
        :rtype: boolean

        """
        if not isinstance(other, BaseElement):  # pragma: no cover
            return False
        return self.as_dict() == other.as_dict() and self._id == other._id

    def __ne__(self, other):
        """
        Check for inequality between two elements.

        :param other: Element to be compared to
        :type other: BaseElement
        :rtype: boolean

        """
        return not self.__eq__(other)  # pragma: no cover

    @classmethod
    def _type_name(cls, manual_name):
        """
        Returns the element name if it has been defined, otherwise it creates it from the module and class name.

        :param manual_name: Name to override the default type name
        :type manual_name: str
        :rtype: str

        """
        pf_name = ''
        if manual_name:
            pf_name = manual_name.lower()
        else:
            camelcase = re.compile(r'([a-z])([A-Z])')
            ccase = lambda s: camelcase.sub(lambda v: '{}_{}'.format(v.group(1), v.group(2).lower()), s)

            pf_name += ccase(cls.__name__)
            pf_name = pf_name.lower()
        return pf_name.lstrip('_')

    def validate_field(self, field_name, val):
        """
        Perform the validations associated with the field with the given name on the value passed.

        :param field_name: The name of property whose validations will be run
        :type field_name: str
        :param val: The value to be validated
        :type val: mixed

        """
        return self._properties[field_name].validate(val)

    def validate(self):
        """Cleans and validates the field values"""
        for name in self._properties.keys():
            #print_("Validating {}...".format(name))
            func_name = 'validate_{}'.format(name)
            val = getattr(self, name)
            #print_("Got {}: func_name: {}, attr: {} ({})".format(name, func_name, val, type(val)))
            if hasattr(self, func_name):
                #print_("Calling custom function: {}".format(func_name))
                val = getattr(self, func_name)(val)
            else:
                #print_("Calling standard function: {}".format(self._properties[name]))
                val = self._properties[name].validate(val)  # self.validate_field(name, val)
            #print_("Validated {}: val: {} ({}), func_name: {}".format(name, val, type(val), func_name))
            setattr(self, name, val)

    def as_dict(self):
        """
        Returns a map of column names to cleaned values

        :rtype: dict

        """
        values = {}
        for name, prop in self._properties.items():
            values[name] = prop.to_database(getattr(self, name, None))
        values.update(self._manual_values)
        return values

    def as_save_params(self):
        """
        Returns a map of property names to cleaned values containing only the properties which should be persisted on
        save.

        :rtype: dict

        """
        values = {}
        was_saved = self._id is not None
        for name, prop in self._properties.items():
            # Determine the save strategy for this column
            prop_strategy = prop.get_save_strategy()

            # Enforce the save strategy
            vm = self._values[name]
            should_save = prop_strategy.condition(previous_value=vm.previous_value,
                                                  value=vm.value,
                                                  has_changed=vm.changed,
                                                  first_save=was_saved,
                                                  graph_property=prop)

            if should_save:
                #print_("Saving %s to database for name %s" % (prop.db_field_name or name, name))
                values[prop.db_field_name or name] = prop.to_database(vm.value)

        # manual values
        for name, prop in self._manual_values.items():
            if prop is None:
                # Remove this property entirely
                values[name] = None
            else:
                # Determine the save strategy
                prop_strategy = prop.strategy
                if prop_strategy.condition(previous_value=prop.previous_value,
                                           value=prop.value,
                                           has_changed=prop.changed,
                                           first_save=was_saved,
                                           graph_property=None):
                    values[name] = prop.value

        return values

    @classmethod
    def translate_db_fields(cls, data):
        """
        Translates field names from the database into field names used in our model

        this is for cases where we're saving a field under a different name than it's model property

        :param data: dict
        :rtype: dict
        """
        dst_data = data.copy().get('_properties', {})
        if data.get('_id', None):
            dst_data.update({'_id': data.copy().get('_id')})
        #print_("Raw incoming data: %s" % data)
        for name, prop in cls._properties.items():
            #print_("trying db_field_name: %s and name: %s" % (prop.db_field_name, name))
            if prop.db_field_name in dst_data:
                dst_data[name] = dst_data.pop(prop.db_field_name)
            elif name in dst_data:
                dst_data[name] = dst_data.pop(name)

        return dst_data

    @classmethod
    def create(cls, *args, **kwargs):
        """Create a new element with the given information."""
        return cls(*args, **kwargs).save()

    def pre_save(self):
        """Pre-save hook which is run before saving an element"""
        self.validate()

    def save(self):
        """
        Base class save method. Performs basic validation and error handling.
        """
        if self.__abstract__:
            raise MogwaiException('cant save abstract elements')
        self.pre_save()
        return self

    def pre_update(self, **values):
        """ Override this to perform pre-update validation """
        pass

    def update(self, **values):
        """
        performs an update of this element with the given values and returns the
        saved object
        """
        if self.__abstract__:
            raise MogwaiException('cant update abstract elements')
        self.pre_update(**values)
        for key in values.keys():
            if key not in self._properties:
                raise TypeError("unrecognized attribute name: '{}'".format(key))

        for k, v in values.items():
            setattr(self, k, v)

        return self.save()

    def _reload_values(self):
        """
        Base method for reloading an element from the database.

        """
        raise NotImplementedError

    def reload(self):
        """
        Reload the given element from the database.

        """
        values = self._reload_values()
        for name, prop in self._properties.items():
            value = values.get(prop.db_field_name, None)
            if value is not None:
                value = prop.to_python(value)
            setattr(self, name, value)
        return self

    @classmethod
    def get_property_by_name(cls, key):
        """
        Get's the db_field_name of a property by key

        :param key: attribute of the model
        :type key: basestring | str
        :rtype: basestring | str | None
        """
        if isinstance(key, string_types):
            prop = cls._properties.get(key, None)
            if prop:
                return prop.db_field_name
        return key  # pragma: no cover

    @classmethod
    def _get_factory(cls):
        if getattr(cls, 'FACTORY_CLASS', None):
            factory_cls = getattr(cls, 'FACTORY_CLASS', None)
            if isinstance(factory_cls, string_types):
                factory_cls = import_string(factory_cls)
            create_cls = factory_cls.create
        else:
            create_cls = cls.create
        
        return create_cls

    def __getitem__(self, item):
        logger.debug("Using __getitem__({})...".format(item))
        #print_("Using __getitem__({})...: options: _properties({}), _manual_values({})".format(item, self._properties.items(), self._manual_values.items()))
        value = self._properties.get(item, None)
        if value is not None:
            # call the normal getattr method
            return getattr(self, item)
        else:
            # manual entry
            value_manager = self._manual_values.get(item, None)
            """ :type value_manager: mogwai.properties.base.BaseValueManager | None """
            if value_manager is None:
                raise AttributeError(item)
            return value_manager.value

    def __setitem__(self, key, value):
        logger.debug("Using __setitem__({}): {}...".format(key, value))
        prop = self._properties.get(key, None)
        if prop is not None:
            # call the normal setattr method
            setattr(self, key, value)
        else:
            # manual entry
            if key in self._manual_values:
                # manual entry already exists, update
                self._manual_values[key].setval(value)
            else:
                # manual entry doesn't exist, create
                from mogwai.properties.base import BaseValueManager
                self._manual_values[key] = BaseValueManager(None, value)

    def __delitem__(self, key):
        logger.debug("Using __delitem__({})...".format(key))
        prop = self._properties.get(key, None)
        if prop is not None:
            # call the normal delattr method
            delattr(self, key)
        else:
            # manual entry
            if key in self._manual_values:
                # manual entry already exists, update for delete
                self._manual_values[key] = None
            else:
                raise AttributeError(key)

    def __contains__(self, item):
        logger.debug("Checking contains...")
        return item in set(self._properties.keys()).union(set(self._manual_values.keys()))

    def __len__(self):
        logger.debug("Getting len...")
        return len(set(self._properties.keys()).union(set(self._manual_values.keys())))

    def __iter__(self):
        logger.debug("Iterating through __iter__...")
        for item in set(self._properties.keys()).union(set(self._manual_values.keys())):
            yield item

    def items(self):
        logger.debug("Iterating through items...")
        items = []
        for key in self._properties.keys():
            items.append((key, getattr(self, key)))
        items.extend([(pair[0], pair[1].value) for pair in self._manual_values.items() if pair[1] is not None])
        return items

    def keys(self):
        logger.debug("Iterating through keys...")
        items = []
        items.extend(self._properties.keys())
        items.extend([k for k in self._manual_values.keys() if self._manual_values.get(k) is not None])
        return items

    def values(self):
        logger.debug("Iterating through values...")
        items = []
        for key in self._properties.keys():
            items.append(getattr(self, key))
        items.extend([v.value for v in self._manual_values.values() if v is not None])
        return items


class ElementMetaClass(type):
    """Metaclass for all graph elements"""

    def __new__(mcs, name, bases, body):
        """
        """
        #move graph property definitions into graph property dict
        #and set default column names
        prop_dict = OrderedDict()
        relationship_dict = OrderedDict()

        #get inherited properties
        for base in bases:
            if body.get('__enum_id_only__', None) is None:
                body['__enum_id_only__'] = getattr(base, '__enum_id_only__', True)
            for k, v in getattr(base, '_properties', {}).items():
                prop_dict.setdefault(k, v)
            for k, v in getattr(base, '_relationships', {}).items():
                relationship_dict.setdefault(k, v)

        #print_("Name: %s\n\tBases: %s\n\tBody: %s" % (name, bases, body.keys()))

        def _transform_property(prop_name, prop_obj):
            prop_dict[prop_name] = prop_obj
            prop_obj.set_property_name(prop_name)
            if prop_obj.db_field_prefix is not None:
                db_field_prefix_name = name.lower()
                prop_obj.set_db_field_prefix(db_field_prefix_name)
            #set properties
            _get = lambda self: self._values[prop_name].getval()
            _set = lambda self, val: self._values[prop_name].setval(val)
            _del = lambda self: self._values[prop_name].delval()
            if prop_obj.can_delete:
                body[prop_name] = property(_get, _set, _del)
            else:  # pragma: no cover
                body[prop_name] = property(_get, _set)

        property_definitions = [(k, v) for k, v in body.items() if isinstance(v, properties.GraphProperty)]
        property_definitions = sorted(property_definitions, #cmp=lambda x, y: cmp(x[1].position, y[1].position),
                                      key=lambda x: x[1].position)

        #TODO: check that the defined graph properties don't conflict with any of the
        #Model API's existing attributes/methods transform column definitions
        for k, v in property_definitions:
            _transform_property(k, v)

        #check for duplicate graph property names
        prop_names = set()
        for v in prop_dict.values():
            if v.db_field_name in prop_names:
                raise ModelException("%s defines the graph property %s more than once" % (name, v.db_field_name))
            prop_names.add(v.db_field_name)

        #create db_name -> model name map for loading
        db_map = {}
        for field_name, prop in prop_dict.items():
            db_map[prop.db_field_name] = field_name

        #add management members to the class
        body['_properties'] = prop_dict
        body['_db_map'] = db_map

        ## Manage relationship attributes
        from mogwai.relationships import Relationship
        from mogwai.tools import LazyImportClass
        for k, v in body.items():
            if isinstance(v, (Relationship, LazyImportClass)):
                relationship_dict[k] = v
        body['_relationships'] = relationship_dict

        #auto link gremlin methods
        gremlin_methods = {}

        #get inherited gremlin methods
        for base in bases:
            for k, v in getattr(base, '_gremlin_methods', {}).items():
                gremlin_methods.setdefault(k, v)

        #short circuit __abstract__ inheritance
        body['__abstract__'] = body.get('__abstract__', False)

        #short circuit path inheritance
        gremlin_path = body.get('gremlin_path')
        body['gremlin_path'] = gremlin_path

        def wrap_method(method):
            def method_wrapper(self, *args, **kwargs):
                return method(self, *args, **kwargs)
            return method_wrapper

        for k, v in body.items():
            if isinstance(v, BaseGremlinMethod):
                gremlin_methods[k] = v
                method = wrap_method(v)
                body[k] = method
                if v.classmethod:
                    body[k] = classmethod(method)
                if v.property:
                    body[k] = property(method)

        body['_gremlin_methods'] = gremlin_methods

        #create the class and add a QuerySet to it
        klass = super(ElementMetaClass, mcs).__new__(mcs, name, bases, body)

        #configure the gremlin methods
        for name, method in gremlin_methods.items():
            method.configure_method(klass, name, gremlin_path)

        _add_model_to_space(klass)
        return klass


@add_metaclass(ElementMetaClass)
class Element(BaseElement):
    #__metaclass__ = ElementMetaClass

    @classmethod
    def deserialize(cls, data):
        """ Deserializes rexpro response into vertex or edge objects """

        dtype = data.get('_type')
        data_id = data.get('_id')
        properties = data.get('_properties')
        if dtype == 'vertex':
            vertex_type = properties['element_type']
            if vertex_type not in vertex_types:
                raise ElementDefinitionException('Vertex "%s" not defined' % vertex_type)

            translated_data = vertex_types[vertex_type].translate_db_fields(data)
            return vertex_types[vertex_type](**translated_data)

        elif dtype == 'edge':
            edge_type = data.get('_label') or properties['_label']
            if edge_type not in edge_types:
                raise ElementDefinitionException('Edge "%s" not defined' % edge_type)

            translated_data = edge_types[edge_type].translate_db_fields(data)
            return edge_types[edge_type](data['_outV'], data['_inV'], **translated_data)

        else:
            raise TypeError("Can't deserialize '%s'" % dtype)
