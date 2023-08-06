
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

import easypackage.setup as setup


# =========================================
#       TEST
# --------------------------------------

class TestCase(helper.TestCase):

    def test__import(self):
        self.assertModule(setup)

    def test_setup(self):
        test = self

        with open(path.join(ROOT_PATH, 'easypackage', 'package.json')) as package_file:
            package_data = json.loads(package_file.read())

        # NOTE: expects `SystemExit` as not sure how to test `setuptools` properly externally.

        with self.assertRaises(BaseException):
            setup.setup('easypackage', verbose = False)

        setup_config = None

        try:
            setup.setup('easypackage', verbose = False)

        except BaseException as error:
            setup_config = error.config

        test.assertTrue(isinstance(package_data, dict))
        test.assertTrue(package_data.get('name', None))
        test.assertTrue(package_data.get('version', None))

        test.assertTrue(isinstance(setup_config, dict))
        test.assertTrue(setup_config.get('name', None))
        test.assertTrue(setup_config.get('version', None))

        test.assertEqual(setup_config.name, package_data['name'])
        test.assertEqual(setup_config.version, package_data['version'])


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':
    helper.run(TestCase)
