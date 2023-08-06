
# =========================================
#       DEPS
# --------------------------------------

import sys
import types
import json

from os import path

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

from easypackage.tests import helper

import easypackage.config as config


# =========================================
#       TEST
# --------------------------------------

class TestCase(helper.TestCase):

    def test__import(self):
        self.assertModule(config)

    def test_config_base(self):
        result = config.config()

        with open(path.join(ROOT_PATH, 'easypackage', 'package.json')) as package_file:
            package_data = json.loads(package_file.read())

        self.assertDeepEqual(result, package_data)

    def test_config_entry(self):
        FOO_ROOT_PATH = helper.fixture_path('packages/py-foo')

        result = config.config('foo', FOO_ROOT_PATH)

        with open(path.join(FOO_ROOT_PATH, 'foo', 'package.json')) as package_file:
            package_data = json.loads(package_file.read())

        self.assertDeepEqual(result, package_data)

    def test_config_entry_nested(self):
        BAR_ROOT_PATH = helper.fixture_path('packages/py-foo/vendor/py-bar')

        result = config.config(BAR_ROOT_PATH)

        with open(path.join(BAR_ROOT_PATH, 'src', 'package.json')) as package_file:
            package_data = json.loads(package_file.read())

        self.assertDeepEqual(result, package_data)


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':
    helper.run(TestCase)
