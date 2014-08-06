from __future__ import unicode_literals
import copy
import warnings

from mogwai.exceptions import ValidationError, MogwaiException
from .strategy import Strategy, SaveAlways, SaveOnce
from .validators import pass_all_validator

DEBUG = False


class BaseValueManager(object):
    """
    Value managers are used to manage values pulled from the database and track state
    changes.

    These are useful for save strategies.
    """

    def __init__(self, graph_property, value, strategy=SaveAlways):
        """
        Initialize the value manager.

        :param graph_property: The graph property to manage
        :type graph_property: mogwai.properties.base.GraphProperty
        :param value: The initial value of the column
        :type value: Object
        :param strategy: The callable condition to compare against. If none given, it won't be used
        :type strategy: mogwai.properties.strategy.Strategy
        """
        self._create_private_fields()

        self.graph_property = graph_property
        self._previous_value = copy.copy(value)
        self.value = value
        self.strategy = strategy
        if not issubclass(self.strategy.__class__, Strategy):
            warnings.warn("Condition is not derived from mogwai.properties.strategy.Strategy and will be ignored!",
                          category=SyntaxWarning)

    def __repr__(self):
        if DEBUG:
            return "%s(property=%s, value=%s, previous_value=%s, strategy=%s)" % (self.__class__.__name__,
                                                                                  self.graph_property,
                                                                                  self.value,
                                                                                  self.previous_value,
                                                                                  self.strategy)
        else:
            return repr(self.value)

    def _create_private_fields(self):
        self._previous_value = None

    @property
    def previous_value(self):
        return self._previous_value

    @previous_value.setter
    def previous_value(self, val):
        self._previous_value = copy.copy(val)

    @property
    def deleted(self):
        """
        Indicates whether or not this value has been deleted.

        :rtype: bool

        """
        return self.value is None and self.previous_value is not None

    @property
    def changed(self):
        """
        Indicates whether or not this value has changed.

        :rtype: bool
        """
        try:
            return self.strategy.condition(self.previous_value,
                                           self.value,
                                           has_changed=(self.value != self.previous_value),
                                           graph_property=self.graph_property)
        except:
            return self.value != self.previous_value

    def getval(self):
        """Return the current value."""
        return self.value

    def setval(self, val):
        """
        Updates the current value.

        :param val: The new value
    :type val: mixed

        """
        self.value = val

    def delval(self):
        """Delete a given value"""
        self.value = None

    def get_property(self):
        """
        Returns a value-managed property attributes

        :rtype: property

        """
        _get = lambda slf: self.getval()
        _set = lambda slf, val: self.setval(val)
        _del = lambda slf: self.delval()

        if self.graph_property.can_delete:
            return property(_get, _set, _del)
        else:
            return property(_get, _set)


class GraphProperty(object):
    """Base class for graph property types"""
    data_type = "Object"
    value_manager = BaseValueManager
    validator = pass_all_validator
    instance_counter = 0

    def __init__(self, description=None, primary_key=False, index=False, index_ext=None, db_field=None, choices=None,
                 default=None, required=False, save_strategy=SaveAlways, unique=None, db_field_prefix=''):
        """
        Initialize this graph property with the given information.

        :param description: description of this field
        :type description: basestring | str
        :param primary_key: Indicates whether or not this is primary key
        :type primary_key: bool
        :param index: Indicates whether or not this field is indexed
        :type index: bool
        :param db_field: The property this field will map to in the database
        :type db_field: basestring | str
        :param choices: A dict of possible choices where the key is the value to store, and the value is the
                        user-friendly value
        :type choices: tuple(tuple(Object, Object)) | list[list[Object, Object]] | None
        :param default: Value or callable with no args to set default value
        :type default: Callable | Number
        :param required: Whether or not this field is required
        :type required: bool
        :param save_strategy: Strategy used when saving the value of the column
        :type save_strategy: strategy.Strategy
        :param unique: Uniqueness constraint left in for backwards compatibility -- used by Spec system.
        :type unique: bool
        :param db_field_prefix: The property prefix associated with the Model.
        :type db_field_prefix: basestring | None

        """
        self.description = description
        self.primary_key = primary_key
        self.index = index
        self.index_ext = index_ext
        self.db_field = db_field
        self.db_field_prefix = db_field_prefix
        self.default = default
        self.required = required
        self.save_strategy = save_strategy
        self.unique = unique
        self.choices = choices

        #the graph property name in the model definition
        self.property_name = None

        #self.value = None

        #keep track of instantiation order
        self.position = GraphProperty.instance_counter
        GraphProperty.instance_counter += 1

    def __repr__(self):
        return "{}(name={}, pos={}, default={}, db_field_name={})".format(self.__class__.__name__,
                                                                          self.property_name,
                                                                          self.position,
                                                                          self.default,
                                                                          self.db_field_name)

    @classmethod
    def get_value_from_choices(cls, value, choices):
        """ Returns the key for the choices tuple of tuples

        Note if you are using classes, they must implement the __in__ and __eq__ for the logical comparison.

        :param value: The raw value to test if it exists in the valid choices. Could be the key or the value in the dict
        :type value: Object
        :rtype: Object
        """
        if not choices:
            return None
        for key, val in choices:
            if value in (key, val):
                return key
        return None

    def validate(self, value):
        """
        Returns a cleaned and validated value. Raises a ValidationError if there's a problem

        :rtype: Object
        """
        if self.choices:
            orig_value = value
            value = GraphProperty.get_value_from_choices(value, self.choices)
            if value is None:
                raise ValidationError('{} - Value `{}` is not in available choices'.format(self.db_field_name, orig_value))
        if value is None:
            if self.has_default:
                return self.validator(self.get_default())
            elif self.required:
                raise ValidationError('{} - None values are not allowed'.format(self.db_field_name))
            else:
                return None
        return self.validator(value)

    def to_python(self, value):
        """
        Converts data from the database into python values raises a ValidationError if the value can't be converted

        :rtype: Object
        """
        return value

    def to_database(self, value):
        """
        Converts python value into database value

        :rtype: Object
        """
        if value is None and self.has_default:
            return self.get_default()
        return value

    @property
    def has_default(self):
        """
        Indicates whether or not this graph property has a default value.

        :rtype: bool
        """
        return self.default is not None

    @property
    def can_delete(self):
        return not self.primary_key

    def should_save(self, first_save=False):
        """
        Indicates whether or not the property should be saved based on it's save strategy.

        :rtype: bool
        """
        return self.get_save_strategy().condition(previous_value=self.value_manager.previous_value,
                                                  value=self.value_manager.value,
                                                  has_changed=self.value_manager.changed,
                                                  first_save=first_save,
                                                  graph_property=self)

    def get_save_strategy(self):
        """
        Returns the save strategy attached to this graph property.

        :rtype: Callable

        """
        return self.save_strategy or (SaveAlways if not self.primary_key else SaveOnce)

    def get_default(self):
        """
        Returns the default value for this graph property if one is available.

        :rtype: Object | None
        """
        if self.has_default:
            if callable(self.default):
                return self.default()
            else:
                return self.default

    def set_property_name(self, name):
        """
        Sets the graph property name during document class construction.

        This value will be ignored if db_field is set in __init__

        :param name: The name of this graph property
        :type name: str
        """
        self.property_name = name

    def set_db_field_prefix(self, prefix, override=False):
        """
        Sets the graph property name prefix during document class construction.
        """
        if not override and not self.db_field_prefix:
            self.db_field_prefix = prefix.rstrip('_') + '_'
            if self.db_field_prefix == '_':
                self.db_field_prefix = ''

    @property
    def has_db_field_prefix(self):
        """
        Determines if a field prefix has already been defined.
        """
        if self.db_field_prefix not in [None, '']:
            return True
        return False

    @property
    def db_field_name(self):
        """
        Returns the name of the mogwai name of this graph property

        :rtype: basestring | str
        """
        return (self.db_field_prefix or '') + (self.db_field or self.property_name or '')