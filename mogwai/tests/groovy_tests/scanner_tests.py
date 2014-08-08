from __future__ import unicode_literals
from mogwai._compat import print_
import os
from nose.plugins.attrib import attr
from mogwai.tests.base import BaseMogwaiTestCase
from mogwai.gremlin.groovy import parse, GroovyImportParser, GroovyFunctionParser,\
    GroovyImport, GroovyFunction, GroovyFileDef


@attr('unit', 'groovy')
class GroovyScannerTest(BaseMogwaiTestCase):
    """
    Test Groovy language scanner
    """

    @classmethod
    def setUpClass(cls):
        cls.groovy_file = os.path.join(os.path.dirname(__file__), 'groovy_test_model.groovy')
        with open(cls.groovy_file, 'r') as f:
            cls.groovy_file_lines = f.readlines()

    def test_parsing_complicated_function(self):
        """ Groovy test parser functionality """
        groovy_file_def = parse(self.groovy_file)
        """ :type groovy_file_def: GroovyFileDef """
        print_(groovy_file_def)
        self.assertIsInstance(groovy_file_def, GroovyFileDef)
        self.assertEqual(groovy_file_def.filename, self.groovy_file)
        self.assertIsInstance(groovy_file_def.imports, (list, tuple))
        self.assertIsInstance(groovy_file_def.functions, (list, tuple))

        for import_def in groovy_file_def.imports:
            if import_def is not None:
                self.assertIsInstance(import_def, GroovyImport)
            print_("Import: {}".format(import_def))

        for func_def in groovy_file_def.functions:
            if func_def is not None:
                self.assertIsInstance(func_def, GroovyFunction)
            print_("Function: {}".format(func_def))

        groovy_funcs = groovy_file_def.functions

        self.assertEqual(len(groovy_funcs[6].body.split('\n')), 8)

        result_map = {x.name: x for x in groovy_funcs}
        self.assertIn('get_self', result_map)
        self.assertIn('return_value', result_map)
        self.assertIn('long_func', result_map)

    def test_parsing_example_function(self):
        test_func = 'def test_func(param1, param2) {\n    def n = null;\n    for (i in x) {\n n=i; \n}\n}\n'
        result = GroovyFunctionParser.parse(test_func)
        self.assertEqual(result.name, 'test_func')
        self.assertListEqual(result.args, ['param1', 'param2'])
        self.assertEqual(result.body, 'def n = null;\n    for (i in x) {\n n=i; \n}')
        self.assertEqual(result.defn, test_func)

    def test_parsing_example_import(self):
        test_import = 'import com.wellaware.test; //this is sample text'
        result = GroovyImportParser.parse(test_import)
        self.assertListEqual(result.comment_list, ['this', 'is', 'sample', 'text'])
        self.assertListEqual(result.import_list, ['import com.wellaware.test;'])
        self.assertListEqual(result.import_strings, ['com.wellaware.test'])

    def test_bad_parse(self):
        result = GroovyImportParser.parse(1)
        self.assertEqual(result, None)

        result = GroovyFunctionParser.parse(1)
        self.assertEqual(result, None)