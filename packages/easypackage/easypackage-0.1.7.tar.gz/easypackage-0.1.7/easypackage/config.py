
# =========================================
#       DEPS
# --------------------------------------

import sys
import os
import json
import six

from os import path

CURRENT_PATH = path.abspath(path.dirname(__file__))
ROOT_PATH = path.abspath(path.join(CURRENT_PATH, '..'))

try:
    try:
        sys.path.remove(CURRENT_PATH)
    except:
        pass

    sys.path.index(ROOT_PATH)

except ValueError:
    sys.path.insert(0, ROOT_PATH)

import json

from easypackage import root as easyroot

from easypackage.utils.banner import banner
from easypackage.utils.structures import AttributeDict


# =========================================
#       FUNCTIONS
# --------------------------------------

DEFAULT_PACKAGE_SOURCE_FOLDER_NAME = 'src'
DEFAULT_PACKAGE_META_FILE_NAME = 'package.json'


# =========================================
#       FUNCTIONS
# --------------------------------------

def config(name = None, search_path = None, silent = False):
    """
    Load project `package.json` config - if present - from specified file/directory path,
    based on common project root file pattern.

    Examples:

        easypackage.config.config('mypackage')
        easypackage.config.config('mypackage', __file__)
        easypackage.config.config('mypackage', './src')

    """

    if isinstance(name, six.string_types):
        if os.sep in name:
            old_search_path = search_path
            search_path = name
            name = old_search_path

    search_path = search_path or name or os.getcwd()
    package_root_path = easyroot.root(search_path)

    package_name = name or __package__ or DEFAULT_PACKAGE_SOURCE_FOLDER_NAME
    package_meta_file_path = path.join(package_root_path, package_name, DEFAULT_PACKAGE_META_FILE_NAME)

    try:
        with open(package_meta_file_path) as package_meta_file:
            package_meta_json = package_meta_file.read()
            package_meta = json.loads(package_meta_json)

        package_meta = AttributeDict(package_meta)

    except Exception as error:
        package_meta_file_path = path.join(package_root_path, DEFAULT_PACKAGE_SOURCE_FOLDER_NAME, DEFAULT_PACKAGE_META_FILE_NAME)

        try:
            with open(package_meta_file_path) as package_meta_file:
                package_meta_json = package_meta_file.read()
                package_meta = json.loads(package_meta_json)

            package_meta = AttributeDict(package_meta)

        except Exception as error:
            raise IOError('Could not load module: `{0}`'.format(package_meta_file_path))

    return package_meta


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':

    with banner(__file__):

        package_name = 'easypackage'

        result = config('easypackage')

        print('config()\n\n  => {0}\n'.format(json.dumps(result, indent = 4)))

        package_name = 'easypackage'
        search_path = '~/Dev/Private/python-easypackage'

        result = config(package_name, search_path)

        print('config("{0}")\n\n  => {1}\n'.format(search_path, json.dumps(result, indent = 4)))
