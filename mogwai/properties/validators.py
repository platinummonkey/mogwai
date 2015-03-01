from __future__ import unicode_literals
import re
try:
    from urllib.parse import urlsplit, urlunsplit
except ImportError:     # Python 2
    from urlparse import urlsplit, urlunsplit

from mogwai._compat import string_types, text_type, float_types, integer_types, array_types, bool_types, print_
from mogwai.exceptions import MogwaiException, ValidationError
import datetime
from pytz import utc
from decimal import Decimal as _D
from collections import Iterable

# These values, if given to validate(), will trigger the self.required check.
EMPTY_VALUES = (None, '', [], (), {})


class BaseValidator(object):
    message = 'Enter a valid value.'
    code = 'invalid'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        """
        Validates that the input passes validation
        """
        return value

pass_all_validator = BaseValidator()


class BooleanValidator(BaseValidator):
    message = 'Enter a valid Boolean.'

    def __call__(self, value):
        if not isinstance(value, bool_types):
            raise ValidationError(self.message, self.code)
        return value

bool_validator = BooleanValidator()


class NumericValidator(BaseValidator):
    message = 'Enter a valid number.'
    data_types = float_types + integer_types + (_D, )

    def __call__(self, value):
        if not isinstance(value, self.__class__.data_types):
            raise ValidationError(self.message, code=self.code)
        return value

numeric_validator = NumericValidator()


class FloatValidator(NumericValidator):
    data_types = float_types


float_validator = FloatValidator()


class DecimalValidator(NumericValidator):
    data_types = float_types + (_D, )


decimal_validator = DecimalValidator()


class IntegerValidator(NumericValidator):
    data_types = integer_types


integer_validator = IntegerValidator()


class LongValidator(NumericValidator):
    data_types = integer_types


long_validator = LongValidator()


class PositiveIntegerValidator(NumericValidator):
    data_types = integer_types

    def __call__(self, value):
        super(PositiveIntegerValidator, self).__call__(value)
        if value < 0:
            raise ValidationError("Value must be 0 or greater")
        return value

positive_integer_validator = PositiveIntegerValidator()


class StringValidator(BaseValidator):
    message = 'Enter a valid string: {}'
    data_type = string_types

    def __call__(self, value):
        if not isinstance(value, self.data_type):
            raise ValidationError(self.message.format(value), code=self.code)
        return value


string_validator = StringValidator()


class ListValidator(BaseValidator):
    message = 'Enter a valid list'
    data_types = array_types

    def __call__(self, value):
        if not isinstance(value, self.data_types):
            raise ValidationError(self.message, code=self.code)
        return value

list_validator = ListValidator()


class DictValidator(BaseValidator):
    message = 'Enter a valid dict'

    def __call__(self, value):
        if not isinstance(value, dict):
            raise ValidationError(self.message, code=self.code)
        return value

dict_validator = DictValidator()


class DateTimeValidator(BaseValidator):
    message = 'Not a valid DateTime: {}'

    def __call__(self, value):
        if not isinstance(value, datetime.datetime) and value is not None:
            raise ValidationError(self.message.format(value), code=self.code)
        return value

datetime_validator = DateTimeValidator()


class DateTimeUTCValidator(BaseValidator):
    message = 'Not a valid UTC DateTime: {}'

    def __call__(self, value):
        super(DateTimeUTCValidator, self).__call__(value)
        if value is None:
            return
        if not isinstance(value, datetime.datetime) and value is not None:
            raise ValidationError(self.message.format(value), code=self.code)
        if value and value.tzinfo != utc:
            #print_("Got value with timezone: {} - {}".format(value, value.tzinfo))
            try:
                value = value.astimezone(tz=utc)
            except ValueError:  # last ditch effort
                try:
                    value = value.replace(tz=utc)
                except (AttributeError, TypeError):
                    raise ValidationError(self.message.format(value), code=self.code)
            except AttributeError:  # pragma: no cover
                # This should never happen, unless it isn't a datetime object
                raise ValidationError(self.message % (value, ), code=self.code)
        #print_("Datetime passed validation: {} - {}".format(value, value.tzinfo))
        return value


datetime_utc_validator = DateTimeUTCValidator()


class RegexValidator(BaseValidator):
    regex = ''

    def __init__(self, regex=None, message=None, code=None):
        super(RegexValidator, self).__init__(message=message, code=code)
        if regex is not None:
            self.regex = regex

        # Compile the regex if it was not passed pre-compiled.
        if isinstance(self.regex, string_types):  # pragma: no cover
            self.regex = re.compile(self.regex)

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        if not self.regex.search(text_type(value)):
            raise ValidationError(self.message, code=self.code)
        else:
            return value


class URLValidator(RegexValidator):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    message = 'Enter a valid URL address: {}'
    code = 'invalid'

    def __call__(self, value):
        try:
            super(URLValidator, self).__call__(value)
        except ValidationError as e:
            # Trivial case failed. Try for possible IDN domain
            if value:
                value = text_type(value)
                scheme, netloc, path, query, fragment = urlsplit(value)
                try:
                    netloc = netloc.encode('idna').decode('ascii')  # IDN -> ACE
                except UnicodeError:  # invalid domain part
                    raise ValidationError(self.message.format(value), code=self.code)
                url = urlunsplit((scheme, netloc, path, query, fragment))
                return super(URLValidator, self).__call__(url)
            else:
                raise ValidationError(self.message.format(value), code=self.code)
        return value


class EmailValidator(RegexValidator):

    regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
        r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)'  # domain
        r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$',  # literal form, ipv4 address (SMTP 4.1.3)
        re.IGNORECASE)

    message = 'Enter a valid email address: {}'
    code = 'invalid'

    def __call__(self, value):
        try:
            super(EmailValidator, self).__call__(value)
        except ValidationError as e:
            # Trivial case failed. Try for possible IDN domain-part
            if value and isinstance(value, string_types) and '@' in value:
                parts = value.split('@')
                try:
                    parts[-1] = parts[-1].encode('idna').decode('ascii')
                except UnicodeError:
                    raise ValidationError(self.message.format(value), code=self.code)
                super(EmailValidator, self).__call__('@'.join(parts))
            else:
                raise ValidationError(self.message.format(value), code=self.code)
        return value

validate_email = EmailValidator()

slug_re = re.compile(r'^[-a-zA-Z0-9_]+$')
validate_slug = RegexValidator(slug_re, "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')

## IPv4
ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')
validate_ipv4_address = RegexValidator(ipv4_re, 'Enter a valid IPv4 address.', 'invalid')

# IPv6
ipv6_re = re.compile(
    r'('
    r'([0-9A-F]{1,4}:){7,7}[0-9A-F]{1,4}|'          # 1:2:3:4:5:6:7:8
    r'([0-9A-F]{1,4}:){1,7}:|'                      # 1::                              1:2:3:4:5:6:7::
    r'([0-9A-F]{1,4}:){1,6}:[0-9A-F]{1,4}|'         # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
    r'([0-9A-F]{1,4}:){1,5}(:[0-9A-F]{1,4}){1,2}|'  # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
    r'([0-9A-F]{1,4}:){1,4}(:[0-9A-F]{1,4}){1,3}|'  # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
    r'([0-9A-F]{1,4}:){1,3}(:[0-9A-F]{1,4}){1,4}|'  # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
    r'([0-9A-F]{1,4}:){1,2}(:[0-9A-F]{1,4}){1,5}|'  # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
    r'[0-9A-F]{1,4}:((:[0-9A-F]{1,4}){1,6})|'       # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8
    r':((:[0-9A-F]{1,4}){1,7}|:)'                   # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::
    r')', re.IGNORECASE)
validate_ipv6_address = RegexValidator(ipv6_re, 'Enter a valid IPv6 address.', 'invalid')


# IPv6/4
ipv64_re = re.compile(
    ipv6_re.pattern[:-1] + r'|' +
    r'::(ffff(:0{1,4}){0,1}:){0,1}'  # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255
    r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}'  # ... (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|'
    r'([0-9a-fA-F]{1,4}:){1,4}:'  # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33 (IPv4-Embedded IPv6 Address)
    r'((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}'
    r'(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
    r')', re.IGNORECASE)

validate_ipv6_ipv4_address = RegexValidator(ipv64_re, 'Enter a valid IPv4, IPv6, '
                                                      '(IPv4-mapped, IPv4 Translated or IPv4-Embedded) IPv6 address',
                                            'invalid')


validate_url = URLValidator()

re_uuid = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
validate_uuid4 = RegexValidator(re_uuid, 'Enter a valid UUID4.', 'invalid')
validate_uuid1 = RegexValidator(re_uuid, 'Enter a valid UUID1.', 'invalid')


float_pattern = r'[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'

geoshape_point_re = re.compile(r'point\[(?P<latitude>' + float_pattern + r'),'
                               r'(?P<longitude>' + float_pattern + r')\]', re.IGNORECASE)
geoshape_box_re = re.compile(r'box\[\[(?P<southwest_latitude>' + float_pattern + r'),'
                             r'(?P<southwest_longitude>' + float_pattern + r')\],'
                             r'\[(?P<northeast_latitude>' + float_pattern + r'),'
                             r'(?P<northeast_longitude>' + float_pattern + r')\]\]', re.IGNORECASE)
geoshape_circle_re = re.compile(r'circle\['
                                r'(?P<latitude>' + float_pattern + r'),'
                                r'(?P<longitude>' + float_pattern + r')\]'
                                r':(?P<radius_in_kilometers>' + float_pattern + r')', re.IGNORECASE)


class GeoShapeObject(object):

    class Types(object):
        point = 'point'
        box = 'box'
        circle = 'circle'

    def __init__(self, geo_type='point', **kwargs):
        if geo_type not in [GeoShapeObject.Types.point, GeoShapeObject.Types.box, GeoShapeObject.Types.circle]:
            raise MogwaiException('Invalid GeoShape type: {}'.format(geo_type))
        self.geo_type = geo_type
        if self.geo_type is GeoShapeObject.Types.point:
            self.latitude = kwargs.get('latitude', None)
            self.longitude = kwargs.get('longitude', None)
        elif self.geo_type is GeoShapeObject.Types.box:
            self.southwest_latitude = kwargs.get('southwest_latitude', None)
            self.southwest_longitude = kwargs.get('southwest_longitude', None)
            self.northeast_latitude = kwargs.get('northeast_latitude', None)
            self.northeast_longitude = kwargs.get('northeast_longitude', None)
        elif self.geo_type is GeoShapeObject.Types.circle:
            self.latitude = kwargs.get('latitude', None)
            self.longitude = kwargs.get('longitude', None)
            self.radius_in_kilometers = kwargs.get('radius_in_kilometers', None)
        if not self.validate():
            raise ValidationError("Invalid GeoShape!: {}(**{})".format(geo_type, kwargs))

    def validate(self):
        number_types = integer_types + float_types
        if self.geo_type is GeoShapeObject.Types.point:
            return isinstance(self.longitude, number_types) and isinstance(self.latitude, number_types)
        elif self.geo_type is GeoShapeObject.Types.box:
            return isinstance(self.southwest_latitude, number_types) and \
                   isinstance(self.southwest_longitude, number_types) and \
                   isinstance(self.northeast_latitude, number_types) and \
                   isinstance(self.northeast_longitude, number_types)
        elif self.geo_type is GeoShapeObject.Types.circle:
            return isinstance(self.latitude, number_types) and \
                   isinstance(self.longitude, number_types) and \
                   isinstance(self.radius_in_kilometers, number_types)

    def _to_database(self):
        if self.geo_type is GeoShapeObject.Types.point:
            return "Geoshape.point({:f},{:f})".format(self.latitude, self.longitude)
        elif self.geo_type is GeoShapeObject.Types.box:
            return "Geoshape.box({:f}, {:f}, {:f}, {:f})".format(self.southwest_latitude, self.southwest_longitude,
                                                                 self.northeast_latitude, self.northeast_longitude)
        elif self.geo_type is GeoShapeObject.Types.circle:
            return "Geoshape.circle({:f}, {:f}, {:f})".format(self.latitude, self.longitude, self.radius_in_kilometers)

    @staticmethod
    def point(latitude, longitude):
        return GeoShapeObject(geo_type=GeoShapeObject.Types.point,
                              latitude=latitude, longitude=longitude)

    @staticmethod
    def _from_rexpro(response):
        if geoshape_point_re.match(response):
            GeoShapeObject.point(**geoshape_point_re.match(response).groupdict())
        elif geoshape_box_re.match(response):
            GeoShapeObject.box(**geoshape_box_re.match(response).groupdict())
        elif geoshape_circle_re.match(response):
            GeoShapeObject.circle(**geoshape_circle_re.match(response).groupdict())

    @staticmethod
    def circle(latitude, longitude, radius_in_kilometers):
        return GeoShapeObject(geo_type=GeoShapeObject.Types.point,
                              latitude=latitude, longitude=longitude, radius_in_kilometers=radius_in_kilometers)

    @staticmethod
    def box(southwest_latitude, southwest_longitude, northeast_latitude, northeast_longitude):
        return GeoShapeObject(geo_type=GeoShapeObject.Types.point,
                              southwest_latitude=southwest_latitude, southwest_longitude=southwest_longitude,
                              northeast_latitude=northeast_latitude, northeast_longitude=northeast_longitude)

    def __repr__(self):
        kwargs = ', '.join(['{}={}'.format(k, v) for k, v in self.__dict__.items() if k != 'geo_type'])
        return '{}(geo_type={}, {})'.format(self.__class__.__name__, self.geo_type, kwargs)

    def __eq__(self, other):
        if not isinstance(other, GeoShapeObject):
            return False
        else:
            return other.__dict__ == self.__dict__


class GeoShapeValidator(BaseValidator):
    message = 'Enter a valid GeoShapeObject.'
    code = 'invalid'

    def __call__(self, value):
        """
        Validates that the input is a GeoShapeObject
        """
        if not isinstance(value, GeoShapeObject):
            raise ValidationError(self.message, code=self.code)
        else:
            if value.validate():
                return value
            else:
                raise ValidationError(self.message, code=self.code)

geoshape_validator = GeoShapeValidator()