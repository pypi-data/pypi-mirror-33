
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

import easypackage.root as root


# =========================================
#       TEST
# --------------------------------------

class TestCase(helper.TestCase):

    def test__import(self):
        self.assertModule(root)

    def test_root_base(self):
        root_path = root.root()

        self.assertEqual(root_path, ROOT_PATH)

        root_path = root.root(helper.fixture_path('packages/null'))

        self.assertEqual(root_path, ROOT_PATH)

    def test_root_entry(self):
        foo_root_path = helper.fixture_path('packages/py-foo')

        root_path = root.root(helper.fixture_path('packages/py-foo'))

        self.assertEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/'))

        self.assertEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo'))

        self.assertEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo/'))

        self.assertEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo'))

        self.assertEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/'))

        self.assertEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo'))

        self.assertEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo/'))

        self.assertEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo/utils'))

        self.assertEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo/utils/'))

        self.assertEqual(root_path, foo_root_path)

    def test_root_entry_pattern(self):
        foo_root_path = helper.fixture_path('packages/py-foo')

        root_path = root.root(helper.fixture_path('packages/py-foo'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo/'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo/'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo/utils'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/foo/utils/'), 'not_a_file')

        self.assertNotEqual(root_path, foo_root_path)

    def test_root_entry_nested(self):
        bar_root_path = helper.fixture_path('packages/py-foo/vendor/py-bar')

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar'))

        self.assertEqual(root_path, bar_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/'))

        self.assertEqual(root_path, bar_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/src'))

        self.assertEqual(root_path, bar_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/src/'))

        self.assertEqual(root_path, bar_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/src/utils'))

        self.assertEqual(root_path, bar_root_path)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/src/utils/'))

        self.assertEqual(root_path, bar_root_path)

    def test_root_entry_nested(self):
        bar_root_path = helper.fixture_path('packages/py-foo/vendor/py-bar')

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar'), 'not_a_file')

        self.assertEqual(root_path, None)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/'), 'not_a_file')

        self.assertEqual(root_path, None)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/src'), 'not_a_file')

        self.assertEqual(root_path, None)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/src/'), 'not_a_file')

        self.assertEqual(root_path, None)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/src/utils'), 'not_a_file')

        self.assertEqual(root_path, None)

        root_path = root.root(helper.fixture_path('packages/py-foo/vendor/py-bar/src/utils/'), 'not_a_file')

        self.assertEqual(root_path, None)


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':
    helper.run(TestCase)
