import collections
import pyparsing
import re


# Cache of parsed files
_parsed_file_cache = {}
GroovyImport = collections.namedtuple('GroovyImport', ['comment_list', 'import_strings', 'import_list'])
GroovyFunction = collections.namedtuple('GroovyFunction', ['name', 'args', 'body', 'defn'])
GroovyFileDef = collections.namedtuple('GroovyFileDefinition', ['functions', 'imports', 'filename'])


class GroovyFunctionParser(object):
    """
    Given a string containing a single function definition this class will parse the function definition and return
    information regarding it.
    """

    # Simple Groovy sub-grammar definitions
    KeywordDef = pyparsing.Keyword('def')
    VarName = pyparsing.Regex(r'[A-Za-z_]\w*')
    FuncName = VarName
    FuncDefn = KeywordDef + FuncName + "(" + pyparsing.delimitedList(VarName) + ")" + "{"

    @classmethod
    def parse(cls, data):
        """
        Parse the given function definition and return information regarding the contained definition.

        :param data: The function definition in a string
        :type data: str | basestring
        :rtype: dict

        """
        try:
            # Parse the function here
            result = cls.FuncDefn.parseString(data)
            result_list = result.asList()
            args = result_list[3:result_list.index(')')]
            # Return single line or multi-line function body
            fn_body = re.sub(r'[^\{]+\{', '', data, count=1)
            parts = fn_body.strip().split('\n')
            fn_body = '\n'.join(parts[0:-1])
            return GroovyFunction(result[1], args, fn_body, data)
        except Exception as ex:
            return None


class GroovyImportParser(object):
    """
    Given a string containing a single import definition this class will parse the import definition and return
    information regarding it.
    """

    # Simple Groovy sub-grammar definitions
    ImportDef = pyparsing.Suppress(pyparsing.Keyword('import'))
    ImportVarName = pyparsing.Regex(r'[A-Za-z_.\*]*')
    CommentVar = pyparsing.Word(pyparsing.alphas, pyparsing.alphanums).setName('comment')
    OptionalSpace = pyparsing.Optional(' ')
    ImportDefn = ImportDef + \
                 pyparsing.delimitedList(ImportVarName, delim='.').setResultsName('imports') + \
                 pyparsing.Suppress(";") + \
                 pyparsing.Optional(
                     pyparsing.Suppress('//') +
                     pyparsing.delimitedList(CommentVar, delim=pyparsing.Empty()).setResultsName('comment')
                 )

    @classmethod
    def parse(cls, data):
        """
        Parse the given import and return information regarding the contained import statement.

        :param data: The import statement in a string
        :type data: str | basestring
        :rtype: dict

        """
        try:
            # Parse the function here
            result = cls.ImportDefn.parseString(data)
            package_list = []
            if 'imports' in result:
                package_list = result['imports'].asList()

            comment_list = []
            if 'comment' in result:
                comment_list = result['comment'].asList()

            return GroovyImport(comment_list,
                                package_list,
                                ['import {};'.format(package) for package in package_list])
        except Exception as ex:
            return None


def parse(filename):
    """
    Parse Groovy code in the given file and return a list of information about each function necessary for usage in
    queries to database.

    :param filename: The file containing groovy code.
    :type filename: str
    :rtype: list

    """
    # Check cache before parsing file
    global _parsed_file_cache
    if filename in _parsed_file_cache:
        return _parsed_file_cache[filename]

    ImportDefnRegexp = r'^import.*'
    FuncDefnRegexp = r'^def.*\{'
    FuncEndRegexp = r'^\}.*$'
    passedFirstFunction = False
    with open(filename, 'r') as f:
        file_lines = [line.rstrip('\n') for line in f.readlines()]
    all_fns = []
    all_imports = []
    fn_lines = ''
    for line in file_lines:
        if not passedFirstFunction and re.match(ImportDefnRegexp, line):
            all_imports.append(line)
        elif len(fn_lines) > 0:
            if re.match(FuncEndRegexp, line):
                fn_lines += line + "\n"
                all_fns.append(fn_lines)
                fn_lines = ''
            else:
                fn_lines += line + "\n"
        elif re.match(FuncDefnRegexp, line):
            fn_lines += line + "\n"
            passedFirstFunction = True

    import_results = [GroovyImportParser.parse(im) for im in all_imports]
    func_results = [GroovyFunctionParser.parse(fn) for fn in all_fns]

    result = GroovyFileDef(func_results, import_results, filename)
    _parsed_file_cache[filename] = result
    return result
