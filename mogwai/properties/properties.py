import copy
import datetime
from calendar import timegm
from decimal import Decimal as _D
import re
import time
import warnings
from mogwai._compat import text_type, string_types, float_types, integer_types, long_, PY3

from uuid import uuid1, uuid4
from uuid import UUID as _UUID

from .base import GraphProperty
from .validators import *


class String(GraphProperty):
    """
    String/CharField property
    """
    data_type = "String"
    validator = string_validator

    def __init__(self, *args, **kwargs):
        required = kwargs.get('required', False)
        self.min_length = kwargs.pop('min_length', 1 if required else None)
        self.max_length = kwargs.pop('max_length', None)
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(String, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value, str):
                return value.decode(self.encoding)
            else:
                return value

    def validate(self, value):
        # Make sure it gets encoded properly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)

        value = super(String, self).validate(value)

        # this should never happen unless the Validator is changed
        if value is None:
            return None

        if self.max_length:
            if len(value) > self.max_length:
                raise ValidationError('{} is longer than {} characters'.format(self.property_name, self.max_length))
        if self.min_length:
            if len(value) < self.min_length:
                raise ValidationError('{} is shorter than {} characters'.format(self.property_name, self.min_length))
        return value

Text = String


class Short(GraphProperty):
    """
    Short Data property type
    """
    data_type = "Short"
    validator = integer_validator

    def to_python(self, value):
        if value is not None:
            return int(value)

    def to_database(self, value):
        value = super(Short, self).to_database(value)
        if value is not None:
            return int(value)


class Integer(GraphProperty):
    """
    Integer Data property type
    """
    data_type = "Integer"
    validator = long_validator

    def to_python(self, value):
        if value is not None:
            try:
                return int(value)
            except:
                return long_(value)

    def to_database(self, value):
        value = super(Integer, self).to_database(value)
        if value is not None:
            return long_(value)


class PositiveInteger(Integer):
    """
    Positive Integer Data property type
    """
    data_type = "Integer"
    validator = positive_integer_validator

    def to_python(self, value):
        if value is not None:
            return long_(value)

    def to_database(self, value):
        value = super(Integer, self).to_database(value)
        if value is not None:
            return long_(value)


class Long(GraphProperty):
    """
    Long Data property type
    """
    data_type = "Long"
    validator = long_validator

    def to_python(self, value):
        if value is not None:
            return long_(value)

    def to_database(self, value):
        value = super(Long, self).to_database(value)
        if value is not None:
            return long_(value)


class PositiveLong(Long):
    """
    Positive Long Data property type
    """
    data_type = "Long"
    validator = positive_integer_validator

    def to_python(self, value):
        if value is not None:
            return long_(value)

    def to_database(self, value):
        value = super(Long, self).to_database(value)
        if value is not None:
            return long_(value)


class DateTimeNaive(GraphProperty):
    """
    DateTime Data property type
    """
    data_type = "Double"
    validator = datetime_validator

    def __init__(self, strict=True, **kwargs):
        """
        Initialize date-time column with the given settings.

        :param strict: Whether or not to attempt to automatically coerce types
        :type strict: boolean

        """
        self.strict = strict
        super(DateTimeNaive, self).__init__(**kwargs)

    def to_python(self, value):
        if isinstance(value, datetime.datetime):
            return value
        return datetime.datetime.fromtimestamp(float(value))

    def to_database(self, value):
        value = super(DateTimeNaive, self).to_database(value)
        if value is None:
            return
        if not isinstance(value, datetime.datetime):
            if not self.strict and isinstance(value, string_types + integer_types + float_types):
                value = datetime.datetime.fromtimestamp(float(value))
            else:
                raise ValidationError("'{}' is not a datetime object".format(value))

        tmp = time.mktime(value.timetuple())  # gives us a float with .0
        # microtime is a 6 digit int, so we bring it down to .xxx and add it to the float TS
        tmp += float(value.microsecond) / 1000000.0
        return tmp


class DateTime(GraphProperty):
    """
    UTC DateTime Data property type
    """
    data_type = "Double"
    validator = datetime_utc_validator

    def __init__(self, strict=True, **kwargs):
        """
        Initialize date-time column with the given settings.

        :param strict: Whether or not to attempt to automatically coerce types
        :type strict: boolean

        """
        self.strict = strict
        super(DateTime, self).__init__(**kwargs)

    def to_python(self, value):
        try:
            if isinstance(value, datetime.datetime):
                if value.tzinfo == utc:
                    return self.validator(value)  # .astimezone(tz=utc)
                else:
                    return self.validator(value).astimezone(tz=utc)
        except:  # pragma: no cover
            # this shouldn't happen unless the validator has changed
            pass
        return datetime.datetime.utcfromtimestamp(float(value)).replace(tzinfo=utc)

    def to_database(self, value):
        value = super(DateTime, self).to_database(value)
        if value is None:
            return
        if not isinstance(value, datetime.datetime):
            if isinstance(value, string_types + integer_types + float_types):
                value = datetime.datetime.utcfromtimestamp(float(value)).replace(tzinfo=utc)
            else:
                raise ValidationError("'{}' is not a datetime object".format(value))

        tmp = timegm(value.utctimetuple())  # gives us an integer of epoch seconds without microseconds
        # microtime is a 6 digit int, so we bring it down to .xxx and add it to the float TS
        tmp += float(value.microsecond) / 1000000.0
        return tmp


class UUID(GraphProperty):
    """Universally Unique Identifier (UUID) type - UUID4 by default"""
    data_type = "String"
    validator = validate_uuid4

    def __init__(self, default=lambda: str(uuid4()), **kwargs):
        self.uuid_version = kwargs.pop('version', 'uuid4').lower()
        if self.uuid_version == 'uuid4':
            self.validator = validate_uuid4
        elif self.uuid_version == 'uuid1':
            self.validator = validate_uuid1

        super(UUID, self).__init__(default=default, **kwargs)

    def to_python(self, value):
        val = super(UUID, self).to_python(value)
        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value, str):
                return value.decode('utf-8')
            else:
                return value

    def to_database(self, value):
        val = super(UUID, self).to_database(value)
        if val is None:
            return
        return str(val)


class Boolean(GraphProperty):
    """
    Boolean Data property type
    """
    data_type = "Boolean"
    validator = bool_validator

    def to_python(self, value):
        return bool(value)

    def to_database(self, value):
        val = super(Boolean, self).to_database(value)
        return bool(val)


class Double(GraphProperty):
    """
    Double Data property type
    """
    data_type = "Double"
    validator = float_validator

    def __init__(self, **kwargs):
        self.db_type = 'double'
        super(Double, self).__init__(**kwargs)

    def to_python(self, value):
        if value is not None:
            return float(value)

    def to_database(self, value):
        value = super(Double, self).to_database(value)
        if value is not None:
            return float(value)


class Float(Double):
    """Float class for backwards compatability / if you really want to"""

    def __init__(self, **kwargs):
        warnings.warn("Float type is deprecated. Please use Double.",
                      category=DeprecationWarning)
        super(Float, self).__init__(**kwargs)


class Decimal(GraphProperty):
    """
    Decimal Data property type
    """
    validator = decimal_validator

    def to_python(self, value):
        val = super(Decimal, self).to_python(value)
        if val is not None:
            return _D(val)

    def to_database(self, value):
        val = super(Decimal, self).to_database(value)
        if val is not None:
            return str(val)


class Dictionary(GraphProperty):
    """
    Dictionary Data property type
    """
    data_type = "HashMap"
    validator = dict_validator


class List(GraphProperty):
    """
    List Data property type
    """
    data_type = "ArrayList"
    validator = list_validator


class URL(GraphProperty):
    """
    URL Data property type
    """
    data_type = "String"
    validator = validate_url

    def __init__(self, *args, **kwargs):
        required = kwargs.get('required', False)
        self.min_length = kwargs.pop('min_length', 1 if required else None)
        self.max_length = kwargs.pop('max_length', None)
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(URL, self).__init__(*args, **kwargs)

    def validate(self, value):
        # Make sure it gets encoded correctly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)

        value = super(URL, self).validate(value)

        # this should never happen unless the validator is customized
        if value in (None, [], (), {}):  # pragma: no cover
            return None

        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value, str):
                return value.decode(self.encoding)

        if self.max_length:
            if len(value) > self.max_length:
                raise ValidationError('{} is longer than {} characters'.format(self.property_name, self.max_length))
        if self.min_length:
            if len(value) < self.min_length:
                raise ValidationError('{} is shorter than {} characters'.format(self.property_name, self.min_length))

        self.validator(value)

        return value


class Email(GraphProperty):
    """
    Email Data property type
    """
    data_type = "String"
    validator = validate_email

    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(Email, self).__init__(*args, **kwargs)

    def validate(self, value):
        # Make sure it gets encoded correctly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)

        value = super(Email, self).validate(value)

        # This should never happen unless the validator is changed
        if value in (None, [], (), {}):  # pragma: no cover
            return None

        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value, str):
                return value.decode(self.encoding)

        # This should never happen unless the validator is changed
        if not isinstance(value, string_types):  # pragma: no cover
            raise ValidationError('%s is not a string' % type(value))

        self.validator(value)

        return value


class IPV4(GraphProperty):
    """
    IPv4 Data property type
    """
    data_type = "String"
    validator = validate_ipv4_address

    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(IPV4, self).__init__(*args, **kwargs)

    def validate(self, value):
        # Make sure it gets encoded correctly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)

        value = super(IPV4, self).validate(value)

        # This should never happen unless the validator is changed
        if value in (None, [], (), {}):  # pragma: no cover
            return None

        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value, str):
                return value.decode(self.encoding)

        # This should never happen unless the validator is changed
        if not isinstance(value, string_types):  # pragma: no cover
            raise ValidationError('%s is not a string' % type(value))

        self.validator(value)

        return value


class IPV6(GraphProperty):
    """
    IPv6 Data property type
    """
    data_type = "String"
    validator = validate_ipv6_address

    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(IPV6, self).__init__(*args, **kwargs)

    def validate(self, value):
        # Make sure it gets encoded correctly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)

        value = super(IPV6, self).validate(value)

        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value, str):
                return value.decode(self.encoding)

        # This shouldn't happend unless the validator is changed
        if value in (None, [], (), {}):  # pragma: no cover
            return None

        # This shouldn't happend unless the validator is changed
        if not isinstance(value, string_types):  # pragma: no cover
            raise ValidationError('%s is not a string' % type(value))

        self.validator(value)

        return value


class IPV6WithV4(GraphProperty):
    """
    IPv6 with Mapped/Translated/Embedded IPv4 Data property type
    """
    data_type = "String"
    validator = validate_ipv6_ipv4_address

    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(IPV6WithV4, self).__init__(*args, **kwargs)

    def validate(self, value):
        # Make sure it gets encoded correctly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)

        value = super(IPV6WithV4, self).validate(value)

        # This shouldn't happend unless the validator is changed
        if value in (None, [], (), {}):  # pragma: no cover
            return None

        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value, str):
                return value.decode(self.encoding)

        # This shouldn't happend unless the validator is changed
        if not isinstance(value, string_types):  # pragma: no cover
            raise ValidationError('%s is not a string' % type(value))

        self.validator(value)

        return value


class Slug(GraphProperty):
    """
    Slug Data property type
    """
    data_type = "String"
    validator = validate_slug

    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(Slug, self).__init__(*args, **kwargs)

    def validate(self, value):
        # Make sure it gets encoded correctly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)

        value = super(Slug, self).validate(value)

        if value in (None, [], (), {}):
            return None

        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value, str):
                return value.decode(self.encoding)

        if not isinstance(value, string_types):
            raise ValidationError('%s is not a string' % type(value))

        self.validator(value)

        return value
