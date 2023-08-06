
# =========================================
#       DEPS
# --------------------------------------

import os
import sys
import inspect
import unittest
import json
import inspect
import pprint
import types

from os import path, environ
from colour_runner.result import ColourTextTestResult
from pygments import highlight, lexers, formatters
from six import string_types

from deepdiff import DeepDiff

CURRENT_PATH = path.abspath(path.dirname(__file__))
ROOT_PATH = path.abspath(path.join(CURRENT_PATH, '..', '..'))

try:
    try:
        sys.path.remove(CURRENT_PATH)
    except:
        pass

    sys.path.index(ROOT_PATH)

except ValueError:
    sys.path.insert(0, ROOT_PATH)

PACKAGE_SOURCE_DIRECTORY = path.basename(ROOT_PATH.strip(os.sep)).replace('python-', '').replace('-', '_') # e.g. `python-foo-bar` => `foo_bar`
PACKAGE_SOURCE_PATH = path.join(ROOT_PATH, PACKAGE_SOURCE_DIRECTORY)

try:
    sys.path.index(PACKAGE_SOURCE_PATH)
except ValueError:
    sys.path.insert(0, PACKAGE_SOURCE_PATH)

TESTS_PATH = CURRENT_PATH
FIXTURES_PATH = path.join(TESTS_PATH, '__fixtures__')

DEFAULT_TEST_ROOT_PATH = path.abspath(path.dirname(__file__))
DEFAULT_TEST_FILE_PATTERN = environ.get('TESTS_PATTERN', 'test_*.py')

print('# =========================================')
print('#       {0}'.format(__name__))
print('# --------------------------------------\n')

print('ROOT_PATH: {0}'.format(ROOT_PATH))
print('CURRENT_PATH: {0}'.format(CURRENT_PATH))
print('PACKAGE_SOURCE: {0}'.format(PACKAGE_SOURCE_DIRECTORY))
print('PACKAGE_SOURCE_PATH: {0}'.format(PACKAGE_SOURCE_PATH))
print('TESTS_PATH: {0}'.format(TESTS_PATH))
print('FIXTURES_PATH: {0}'.format(FIXTURES_PATH))
print('DEFAULT_TEST_ROOT_PATH: {0}'.format(DEFAULT_TEST_ROOT_PATH))
print('DEFAULT_TEST_FILE_PATTERN: {0}'.format(DEFAULT_TEST_FILE_PATTERN))

print('\n# --------------------------------------')


# =========================================
#       HELPERS
# --------------------------------------

# See: https://www.pythonsheets.com/notes/python-tests.html

def run(test):
    loader = unittest.TestLoader()

    if isinstance(test, string_types):
        test_path = test

        if path.isfile(test_path):
            test_path = path.dirname(test_path)

        test = suite(path.abspath(test_path))

    if isinstance(test, unittest.TestSuite):
        _suite = test

    else:
        _suite = unittest.TestSuite()

        if isinstance(test, list):
            tests = test

        else:
            tests = [test]

        for test in tests:
            _suite.addTests(loader.loadTestsFromTestCase(test))

    print('')

    unittest.runner.TextTestRunner(verbosity = 2, resultclass = ColourTextTestResult).run(_suite)

def suite(root = DEFAULT_TEST_ROOT_PATH, pattern = DEFAULT_TEST_FILE_PATTERN):
    root = root or DEFAULT_TEST_ROOT_PATH
    pattern = pattern or DEFAULT_TEST_FILE_PATTERN

    suite = unittest.TestSuite()

    for tests in unittest.defaultTestLoader.discover(root, pattern = pattern):
        for test in tests:
            # suite.addTests(test)

            # if isinstance(test, unittest.suite.TestSuite):
            #     suite.addTests(test)

            try:
                suite.addTests(test)

            except Exception as error:
                raise ValueError('Failed to load tests - module import issue? {}'.format(tests))

    return suite

def load(root = DEFAULT_TEST_ROOT_PATH, pattern = DEFAULT_TEST_FILE_PATTERN):
    root = root or DEFAULT_TEST_ROOT_PATH
    pattern = pattern or DEFAULT_TEST_FILE_PATTERN

    unittest.defaultTestLoader.discover(root, pattern = pattern)

def deepdiff(a, b):
    return DeepDiff(a, b, ignore_order = True, report_repetition = True)

def pretty(data):
    result = json.dumps(data, default = lambda x: repr(x), indent = 4, sort_keys = True)
    result = unicode(result, 'UTF-8')
    result = highlight(result, lexers.JsonLexer(), formatters.TerminalFormatter())

    return result

def fixture_path(relative_file_path = None):
    path_parts = filter(lambda value: value is not None, [FIXTURES_PATH, relative_file_path])
    return path.abspath(path.join(*path_parts))

def fixture_file(relative_file_path, *args, **kvargs):
    fixture_file_path = fixture_path(relative_file_path)

    return open(fixture_file_path, *args, **kvargs)

def fixture(relative_file_path, *args, **kvargs):
    return fixture_file(relative_file_path, *args, **kvargs)

def assertModule(result, expression):
    is_string = isinstance(result.__file__, string_types)

    if not is_string:
        raise AssertionError('module path `{0}` expected to be a string - {1}'.format(result, expression and '- {0}'.format(expression) or ''))

    module_file_path = result.__file__

    is_source_file = (module_file_path.find('/{0}'.format(PACKAGE_SOURCE_DIRECTORY)) > -1) # ensure module is loaded from `src`

    if not is_source_file:
        raise AssertionError('module path `{0}` expected to include `{1}` {2}'.format(module_file_path, PACKAGE_SOURCE_DIRECTORY, expression and '- {0}'.format(expression) or ''))

    module_type = type(result)

    is_module = (module_type == types.ModuleType)

    if not is_module:
        raise AssertionError('module `{0}` expected to include `{1}` {2}'.format(module_file_path, PACKAGE_SOURCE_DIRECTORY, expression and '- {0}'.format(expression) or ''))

def assertDeepEqual(result, expected, expression = None):
    # HACK: `deepdiff` works differently on Python 2 vs Python 3 :'(
    result = json.loads(json.dumps(result, default = lambda x: repr(x)))
    expected = json.loads(json.dumps(expected, default = lambda x: repr(x)))

    diff = deepdiff(result, expected)

    if diff != {}:
        raise AssertionError('\n\n%s\nshould deep equal\n\n%s\ndiff:\n\n%s' % (pretty(result), pretty(expected), pretty(diff)))

    return True

def assertNotDeepEqual(result, expected, expression = None):
    # HACK: `deepdiff` works differently on Python 2 vs Python 3 :'(
    result = json.loads(json.dumps(result, default = lambda x: repr(x)))
    expected = json.loads(json.dumps(expected, default = lambda x: repr(x)))

    diff = deepdiff(result, expected)


    if diff == {}:
        raise AssertionError('\n\n%s\nshould deep equal\n\n%s\ndiff:\n\n%s' % (pretty(result), pretty(expected), pretty(diff)))

    return True

class assertNotRaises(unittest.TestCase):

    def __init__(self, exception, expression):
        self.exception = exception
        self.expression = expression

    def __enter__(self):
        if self.exception is None:
            try:
                self.expression()

            except:
                info = sys.exc_info()

                self.fail('%s raised' % repr(info[0]))

        else:
            self.assertRaises(self.exception, self.expression)

    def __exit__(self, type, value, traceback):
        pass

# See: https://stackoverflow.com/questions/4319825/python-unittest-opposite-of-assertraises
class TestCase(unittest.TestCase):

    maxDiff = None

    def assertNotRaises(self, exception, expression = None):
        return assertNotRaises(exception, expression)

    def assertDeepEqual(self, result, expected, expression = None):
        return assertDeepEqual(result, expected, expression)

    def assertNotDeepEqual(self, result, expected, expression = None):
        return assertNotDeepEqual(result, expected, expression)

    def assertModule(self, result, expression = None):
        return assertModule(result, expression)
