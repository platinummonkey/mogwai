from __future__ import unicode_literals
from mogwai._compat import print_, PY2
from mogwai.tests import BaseMogwaiTestCase, testcase_docstring_sub
from mogwai.properties.validators import *
from nose.plugins.attrib import attr
from decimal import Decimal as _D
import datetime
from pytz import utc


@attr('unit', 'validators')
class ValidatorBaseClassTestCase(BaseMogwaiTestCase):
    """ Test Base Validator Callables """
    klass = BaseValidator()
    good_cases = ('', 'a', 1, 1.1, None, [], [1], {}, {'a': 1})
    bad_cases = ()

    def test_callable(self):
        """ Test that the validator is callable """
        self.assertTrue(issubclass(self.klass.__class__, BaseValidator))
        # test validator is callable
        self.assertTrue(callable(self.klass))

    def test_good_validation(self):
        for case in self.good_cases:
            print_("testing case: {}".format(case))
            self.assertNotRaise(self.klass, case)

    def test_bad_validation(self):
        for case in self.bad_cases:
            print_("testing case: {}".format(case))
            self.assertRaises(ValidationError, self.klass, case)


@attr('unit', 'validators')
class BooleanValidatorTestCase(ValidatorBaseClassTestCase):
    """ Boolean Validator """
    klass = BooleanValidator()
    good_cases = (True, False)
    bad_cases = (0, 1.1, 'val', [], (), {}, None)


@attr('unit', 'validators')
class NumericValidatorTestCase(ValidatorBaseClassTestCase):
    klass = NumericValidator()
    if PY2:
        good_cases = (0, 1.1, long(1), True, False)
    else:
        good_cases = (0, 1.1, True, False)
    bad_cases = ('val', [], (), {}, None)


@attr('unit', 'validators')
class FloatValidatorTestCase(ValidatorBaseClassTestCase):
    klass = FloatValidator()
    good_cases = (1.1, )
    if PY2:
        bad_cases = ('val', [], (), {}, None, 0, long(1), False)
    else:
        bad_cases = ('val', [], (), {}, None, 0, False)


@attr('unit', 'validators')
class DecimalValidatorTestCase(FloatValidatorTestCase):
    klass = DecimalValidator()
    good_cases = (1.1, _D(1.1))


@attr('unit', 'validators')
class IntegerValidatorTestCase(ValidatorBaseClassTestCase):
    klass = IntegerValidator()
    if PY2:
        good_cases = (1, long(1), False, True)
    else:
        good_cases = (1, False, True)
    bad_cases = ('val', [], (), {}, None, 0.1)


@attr('unit', 'validators')
class LongValidatorTestCase(ValidatorBaseClassTestCase):
    klass = LongValidator()
    if PY2:
        good_cases = (1, long(2), True, False)
    else:
        good_cases = (1, True, False)
    bad_cases = ('val', [], (), {}, None)


@attr('unit', 'validators')
class PositiveIntegerValidatorTestCase(ValidatorBaseClassTestCase):
    klass = PositiveIntegerValidator()
    if PY2:
        good_cases = (1, long(2), True, False)
        bad_cases = ('val', [], (), {}, None, -1, long(-2))
    else:
        good_cases = (1, True, False)
        bad_cases = ('val', [], (), {}, None, -1)


@attr('unit', 'validators')
class StringValidatorTestCase(ValidatorBaseClassTestCase):
    klass = StringValidator()
    good_cases = ('val', )
    if PY2:
        bad_cases = (1.1, [], (), {}, None, 0, long(1), False)
    else:
        bad_cases = (1.1, [], (), {}, None, 0, False)


@attr('unit', 'validators')
class ListValidatorTestCase(ValidatorBaseClassTestCase):
    klass = ListValidator()
    good_cases = ([], ['val'], (), tuple('val'))
    if PY2:
        bad_cases = ('val', {}, None, 0, long(1), False)
    else:
        bad_cases = ('val', {}, None, 0, False)


@attr('unit', 'validators')
class DictValidatorTestCase(ValidatorBaseClassTestCase):
    klass = DictValidator()
    good_cases = ({}, {'value': 1})
    if PY2:
        bad_cases = ('val', [], (), None, 0, long(1), False, 1.1)
    else:
        bad_cases = ('val', [], (), None, 0, False, 1.1)


@attr('unit', 'validators')
class DateTimeValidatorTestCase(ValidatorBaseClassTestCase):
    klass = DateTimeValidator()
    good_cases = (datetime.datetime.now(), None)
    if PY2:
        bad_cases = ('val', [], (), {}, 0, long(1), False, 1.1)
    else:
        bad_cases = ('val', [], (), {}, 0, False, 1.1)


@attr('unit', 'property')
class DateTimeUTCValidatorTestCase(ValidatorBaseClassTestCase):
    klass = DateTimeUTCValidator()
    good_cases = (datetime.datetime.now(tz=utc), None)
    if PY2:
        bad_cases = ('val', [], (), {}, 0, long(1), False, 1.1, datetime.datetime.now())
    else:
        bad_cases = ('val', [], (), {}, 0, False, 1.1, datetime.datetime.now())


@attr('unit', 'validators')
class URLValidatorTestCase(ValidatorBaseClassTestCase):
    """ URL Validator """

    klass = URLValidator()
    good_cases = ('http://subdomain.domain.com/',
                  'https://domain.com/',
                  'http://domain.com/path/',
                  'http://domain.com/path/?params=1',
                  'http://subdomain.com/path/deep/?params=2&second=3')
    bad_cases = ('htp://fail.com',
                 'fail.com/path/',
                 '/asdf/')


@attr('unit', 'validators')
class EmailValidatorTestCase(ValidatorBaseClassTestCase):
    """ Email Validator """

    klass = EmailValidator()
    good_cases = ('test@test.com', 'test-alice@subdomain.domain.com')
    bad_cases = ('', 'bob', '@test.com', 'bob@test')


@attr('unit', 'validators')
class SlugValidatorTestCase(ValidatorBaseClassTestCase):
    """ Slug Validator """

    klass = validate_slug
    good_cases = ('ab', '12', 'ab12', '12ab')
    bad_cases = ('@', 'a!', '12!', 'ab12!')


@attr('unit', 'validators')
class IPV4ValidatorTestCase(ValidatorBaseClassTestCase):
    """ IPV4 Validator """

    klass = validate_ipv4_address
    good_cases = ('1.2.3.4', '0.0.0.0', '255.255.255.255')
    bad_cases = ('0', '0.', '0.0', '0.0.', '0.0.0', '0.0.0.', '256.256.256.256', '1.2.3.256')


@attr('unit', 'validators')
class IPV6ValidatorTestCase(ValidatorBaseClassTestCase):
    """ IPV6 Validator """

    klass = validate_ipv6_address
    good_cases = ('1:2:3:4:5:6:7:8', '1::', '1:2:3:4:5:6:7::',
                  '1::8', '1:2:3:4:5:6::8', '1:2:3:4:5:6::8',
                  '1::7:8', '1:2:3:4:5::7:8', '1:2:3:4:5::8',
                  '1::6:7:8', '1:2:3:4::6:7:8', '1:2:3:4::8',
                  '1::5:6:7:8', '1:2:3::5:6:7:8', '1:2:3::8',
                  '1::4:5:6:7:8', '1:2::4:5:6:7:8', '1:2::8',
                  '1::3:4:5:6:7:8', '1::3:4:5:6:7:8', '1::8',
                  '::2:3:4:5:6:7:8', '::2:3:4:5:6:7:8', '::8', '::')
    bad_cases = ('0', '0.', '0.0', '0.0.', '0.0.0', '0.0.0.', '256.256.256.256', '1.2.3.256')


@attr('unit', 'validators')
class IPV6With4ValidatorTestCase(ValidatorBaseClassTestCase):
    """ IPv4 mapped/translated/embedded IPv6 Validator """

    klass = validate_ipv6_ipv4_address
    good_cases = ('1:2:3:4:5:6:7:8', '1::', '1:2:3:4:5:6:7::',  # IPv6
                  '1::8', '1:2:3:4:5:6::8', '1:2:3:4:5:6::8',
                  '1::7:8', '1:2:3:4:5::7:8', '1:2:3:4:5::8',
                  '1::6:7:8', '1:2:3:4::6:7:8', '1:2:3:4::8',
                  '1::5:6:7:8', '1:2:3::5:6:7:8', '1:2:3::8',
                  '1::4:5:6:7:8', '1:2::4:5:6:7:8', '1:2::8',
                  '1::3:4:5:6:7:8', '1::3:4:5:6:7:8', '1::8',
                  '::2:3:4:5:6:7:8', '::2:3:4:5:6:7:8', '::8', '::',
                  '::255.255.255.255', '::ffff:255.255.255.255', '::ffff:0:255.255.255.255',  # Mapped/Translated
                  '2001:db8:3:4::192.0.2.33', '64:ff9b::192.0.2.33',  # Embedded
                  )
    bad_cases = ('0', '0.', '0.0', '0.0.', '0.0.0', '0.0.0.', '256.256.256.256', '1.2.3.256', '1.2.3.4')


@attr('unit', 'validators')
class UUID4ValidatorTestCase(ValidatorBaseClassTestCase):
    klass = validate_uuid4
    good_cases = ('bb19eaed-c946-4cef-8001-7cc3357cc439', )
    if PY2:
        bad_cases = ('val', [], (), {}, None, 0, long(1), False, 1.1)
    else:
        bad_cases = ('val', [], (), {}, None, 0, False, 1.1)


@attr('unit', 'validators')
class UUID1ValidatorTestCase(UUID4ValidatorTestCase):
    klass = validate_uuid1