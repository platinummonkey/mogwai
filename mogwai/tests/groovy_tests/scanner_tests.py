from __future__ import unicode_literals
import os
from nose.plugins.attrib import attr
from mogwai.tests.base import BaseMogwaiTestCase
from mogwai.gremlin import parse


@attr('unit', 'groovy')
class GroovyScannerTest(BaseMogwaiTestCase):
    """
    Test Groovy language scanner
    """

    def test_parsing_complicated_function(self):
        """ Groovy test parser functionality """
        groovy_file = os.path.join(os.path.dirname(__file__), 'groovy_test_model.groovy')
        result = parse(groovy_file)
        self.assertEqual(len(result[6].body.split('\n')), 8)

        result_map = {x.name: x for x in result}
        self.assertIn('get_self', result_map)
        self.assertIn('return_value', result_map)
        self.assertIn('long_func', result_map)