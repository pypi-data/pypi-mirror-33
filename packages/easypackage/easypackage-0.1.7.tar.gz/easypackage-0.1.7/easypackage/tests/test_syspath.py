
# =========================================
#       DEPS
# --------------------------------------

import sys
import types

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

import easypackage.syspath as syspath


# =========================================
#       TEST
# --------------------------------------

class TestCase(helper.TestCase):

    def test__import(self):
        self.assertModule(syspath)

    def test_syspath_base(self):
        try:
            sys.path.remove(ROOT_PATH)
        except:
            pass

        added, root_path = syspath.syspath()

        self.assertEqual(added, True) # root
        self.assertEqual(root_path, ROOT_PATH)

        added, root_path = syspath.syspath()

        self.assertEqual(added, False)
        self.assertEqual(root_path, ROOT_PATH)

        try:
            sys.path.remove(root_path)
        except:
            pass

        added, root_path = syspath.syspath()

        self.assertEqual(added, True)
        self.assertEqual(root_path, ROOT_PATH)

    def test_syspath_entry(self):
        FOO_ROOT_PATH = helper.fixture_path('packages/py-foo')

        try:
            sys.path.remove(FOO_ROOT_PATH)
        except:
            pass

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo'))

        self.assertEqual(added, True)
        self.assertEqual(root_path, FOO_ROOT_PATH)

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo'))

        self.assertEqual(added, False)
        self.assertEqual(root_path, FOO_ROOT_PATH)

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo/foo'))

        self.assertEqual(added, False)
        self.assertEqual(root_path, FOO_ROOT_PATH)

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo/foo'))

        self.assertEqual(added, False)
        self.assertEqual(root_path, FOO_ROOT_PATH)

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo'))

        self.assertEqual(added, False)
        self.assertEqual(root_path, FOO_ROOT_PATH)

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo/foo'))

        self.assertEqual(added, False)
        self.assertEqual(root_path, FOO_ROOT_PATH)

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo/foo/utils'))

        self.assertEqual(added, False)
        self.assertEqual(root_path, FOO_ROOT_PATH)

    def test_syspath_entry_nested(self):
        BAR_ROOT_PATH = helper.fixture_path('packages/py-foo/vendor/py-bar')

        try:
            sys.path.remove(BAR_ROOT_PATH)
        except:
            pass

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo/vendor/py-bar'))

        self.assertEqual(added, True)
        self.assertEqual(root_path, BAR_ROOT_PATH)

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo/vendor/py-bar/src'))

        self.assertEqual(added, False)
        self.assertEqual(root_path, BAR_ROOT_PATH)

        added, root_path = syspath.syspath(helper.fixture_path('packages/py-foo/vendor/py-bar/src/utils'))


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':
    helper.run(TestCase)
