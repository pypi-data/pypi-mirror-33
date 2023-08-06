
# =========================================
#       DEPS
# --------------------------------------

import sys
import os

from os import path
from six import PY2, PY3

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

import setuptools
import json

from setuptools import find_packages

from easypackage.config import config as easyconfig
from easypackage.root import root as easyroot

from easypackage.utils.banner import banner
from easypackage.utils.structures import AttributeDict
from easypackage.utils.legacy.dict import bytes2str


# =========================================
#       FUNCTIONS
# --------------------------------------

def setup(name, search_path = None, argv = [], verbose = True):

    """
    Setup helper for Python packages.

    Requires `package.json` project config in package module root.

    Examples:

        easypackage.root.root('mypackage')
        easypackage.root.root('mypackage', __file__)
        easypackage.root.root('mypackage', './src')

    """

    search_path = search_path or name

    project_path = easyroot(search_path)
    setup_config = config(name, project_path, verbose = verbose)

    if not len(argv):
        argv = [__file__]

    # HACK: `setuptools.setup` will fail if `sys.argv` is empty
    sys.argv = argv

    try:
        setuptools.setup(**setup_config)

    except SystemExit as error:
        error.__setattr__('config', setup_config)

        raise error

def config(name, project_path = None, verbose = True):

    with banner('PACKAGE:', enabled = verbose):
        pkg = config_package(project_path)

        if verbose:
            print('pkg', pkg)

    with banner('README:', enabled = verbose):
        readme = config_readme(project_path, pkg = pkg, verbose = verbose)

    with banner('EXCLUDES:', enabled = verbose):
        excludes = config_excludes(project_path, pkg = pkg, verbose = verbose)

    with banner('PACKAGE SOURCE:', enabled = verbose):
        package_source_path = config_package_source(project_path, pkg = pkg, verbose = verbose)

    with banner('PACKAGES:', enabled = verbose):
        packages = config_packages(project_path, pkg = pkg, excludes = excludes, verbose = verbose)

    with banner('PACKAGE FILES:', enabled = verbose):
        package_files = config_package_files(project_path, pkg = pkg, verbose = verbose)

    with banner('DEPENDENCIES:', enabled = verbose):
        dependencies = config_dependencies(project_path, pkg = pkg, verbose = verbose)

    with banner('SCRIPTS:', enabled = verbose):
        scripts = config_scripts(project_path, pkg = pkg, verbose = verbose)

    with banner('CONFIG:', enabled = verbose, close = True):
        name = pkg.get('name', None)

        if PY2:
            name = name.encode('ascii', 'ignore')

        package_data = {}
        package_data[name] = package_files

        package_dir = {}
        package_dir[name] = package_source_path

        version = pkg.get('version', None)
        description = pkg.get('description', None)
        keywords = ' '.join(pkg.get('keywords', []))
        author = pkg.get('author', None)
        url = pkg.get('homepage', None)
        repository = pkg.get('repository', {}).get('url', None)
        bugs = pkg.get('bugs', {}).get('url', None)
        download_url = repository
        license = pkg.get('license', None)
        long_description_content_type = 'text/markdown'
        setup_requires = []
        tests_require = []
        extras_require = {}
        zip_safe = False
        classifiers = []

        config = bytes2str({
            'name': name,
            'version': version,
            'description': description,
            'keywords': keywords,
            'author': author,
            'url': url,
            'project_urls': {
                'repository': repository,
                'bugs': bugs,
            },
            'download_url': download_url,
            'license': license,
            'long_description': readme,
            'long_description_content_type': long_description_content_type,
            'scripts': scripts,
            'packages': packages,
            'package_data': package_data,
            'package_dir': package_dir,
            'install_requires': dependencies,
            'setup_requires': setup_requires,
            'tests_require': tests_require,
            'extras_require': extras_require,
            'zip_safe': zip_safe,
            'classifiers': classifiers,
        })

        config = AttributeDict(config)

        if verbose:
            print(json.dumps(config, default = lambda x: repr(x), indent = 4, sort_keys = False))

    return config

def config_package(project_path, verbose = True):
    pkg = None

    try:
        pkg = easyconfig(project_path, silent = False)

        name = pkg.get('name')

        # if isinstance(name, six.string_types):
        #     pkg['name'] = name.encode('ascii', 'ignore')

        # print(json.dumps(pkg, default = lambda x: repr(x), indent = 4))
        if verbose:
            print(type(pkg))

    except Exception as error:
        message = 'Could not load package config: {0}'.format(error)

        if verbose:
            print('ERROR: {0}'.format(message))

    return pkg

def config_readme(project_path, pkg = {}, verbose = True):
    readme = None

    try:
        readme_file_path = path.join(project_path, 'README.md')

        if verbose:
            print(readme_file_path)

        with open(readme_file_path) as readme_file:
            readme = readme_file.read()

    except Exception as error:
        message = 'ERROR: Could not load `README.md`: {0}'.format(error)

        if verbose:
            print('ERROR: {0}'.format(message))

    return readme

def config_excludes(project_path, pkg = {}, verbose = True):
    excludes = pkg.get('exclude', [])

    for exclude in excludes:
        if verbose:
            print(exclude)

    return excludes

def config_package_source(project_path, pkg = {}, verbose = True):
    package_source_path = pkg.get('directories', {}).get('lib', pkg.get('directories', {}).get('name'))

    return package_source_path

def config_packages(project_path, pkg = {}, excludes = [], verbose = True):
    package_source_path = pkg.get('directories', {}).get('lib', pkg.get('directories', {}).get('name'))

    packages = find_packages(exclude = excludes)
    packages = filter(lambda package: package.find(package_source_path) > -1, packages)
    packages = map(lambda package: str.replace(package, package_source_path, str(pkg['name'])), packages)
    packages = list(packages)

    for package in packages:
        if verbose:
            print(package)

    return packages

def config_package_files(project_path, pkg = {}, verbose = True):
    package_source_path = pkg.get('directories', {}).get('lib', pkg.get('directories', {}).get('name'))

    package_files = []

    for (_path, _directories, _filenames) in os.walk(package_source_path):
        for _filename in _filenames:
            package_files.append(path.abspath(path.join('..', _path, _filename)))

    for package_file in package_files:
        if verbose:
            print(package_file)

    return package_files

def config_dependencies(project_path, pkg = {}, verbose = True):
    dependencies = []

    with open(path.join(ROOT_PATH, 'requirements.txt')) as file:
        try:
            for line in file.read().splitlines():
                dependency = line.strip().split('=')[0]

                if len(dependency):
                    dependencies.append(dependency)

        except Exception as error:
            if verbose:
                print('ERROR: Could not load `requirements.txt`: %s' % (error))


    for dependency in dependencies:
        if verbose:
            print(dependency)

    return dependencies

def config_scripts(project_path, pkg = {}, verbose = True):
    scripts = []

    pkg['bin'] = pkg.get('bin', {})

    for bin_name, bin_path in pkg['bin'].items():
        scripts.append(bin_path)

    return scripts


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':

    with banner(__file__):

        search_path = path.abspath(path.normpath(sys.argv.pop() or path.dirname(__file__)))
        # result = setup('easypackage', search_path, argv = sys.argv)
        # result = setup('easypackage', argv = sys.argv)
        result = setup('markable_utils', '/Users/grimen/Dev/Markable/markable-python-utils')

        print('\nsetup({0}, argv = {1})\n\n  => {2}'.format(search_path, sys.argv, result))

