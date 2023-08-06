
import setuptools

# DISABLED/BUG: this line fails when `pip install easypackage` but works `pip install .`
# from easypackage import __version__

setuptools.setup(
    name = 'easypackage',
    version = '0.1.8',
    description = (
        'Python packages - the simple way.'
    ),
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    keywords = [
        'python',
        'package',
        'module',
        'easy',
        'automatic',
        'syspath',
        'setup',
        'release',
        'root',
    ],
    author = 'Jonas Grimfelt',
    author_email = 'grimen@gmail.com',
    url = 'https://github.com/grimen/python-easypackage',
    download_url = 'https://github.com/grimen/python-easypackage',
    project_urls = {
        'repository': 'https://github.com/grimen/python-easypackage',
        'bugs': 'https://github.com/grimen/python-easypackage/issues',
    },
    packages = setuptools.find_packages(),
    package_dir = {
        'easypackage': 'easypackage'
    },
    package_data = {
        '': [
            'MIT-LICENSE',
            'README.md',
        ],
        'easypackage': [
            '*.*',
        ]
    },
    py_modules = ['easypackage'],
    license = 'MIT',
    classifiers = [
        'Topic :: Software Development :: Libraries',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    zip_safe = True,
)
