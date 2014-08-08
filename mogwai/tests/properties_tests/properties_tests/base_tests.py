from __future__ import unicode_literals
from mogwai.tests import BaseMogwaiTestCase
from mogwai.properties import GraphProperty
from nose.plugins.attrib import attr
from mogwai.exceptions import ValidationError
from mogwai._compat import print_


@attr('unit', 'property')
class GraphPropertyBaseClassTestCase(BaseMogwaiTestCase):
    """ Test Base Strategy Callable Object """
    klass = GraphProperty
    good_cases = ('', 'a', 1, 1.1, None, [], [1], {}, {'a': 1})
    bad_cases = ()

    def test_subclass(self):
        """ Test if Property is a GraphProperty """
        self.assertIsSubclass(self.klass, GraphProperty)

    def test_validation(self):
        for case in self.good_cases:
            print_("testing good case: {}".format(case))
            self.assertNotRaise(self.klass().validate, case)

        for case in self.bad_cases:
            print_("testing bad case: {}".format(case))
            self.assertRaises(ValidationError, self.klass().validate, case)
