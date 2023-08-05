
# Easy Package - for Python [![Build Status](https://travis-ci.org/grimen/python-easypackage.svg?branch=master)](https://travis-ci.org/grimen/python-easypackage)

Python packages - the simple way.


## Background

**Had to code Python** so ended up abstracting out these Python package related utilities to be able to deal with Python packages which is in a sad state in comparison to most other language environments.


## Features

- **Easy package setup scripts** - because manual Python `setup.py` scripts breaks "convention of over configuration" principle, as well as a bunch of other software design patterns.

- **Easy package (system) load paths** - because package imports and load paths in Python makes adults cry.

- **Easy package tag/release** - because package tag/release management should not be done by hand, fallback on conventions.


## Install

Install using **pip**:

```sh
pip install easypackage
```


## Usage

How to to make use of `easypackage` in various ways:


### Required

Create a `package.json` - according to **Node.js** specification.


### Easy package setup

In file `setup.py` in package project root:

```python
import sys

from easypackage import setup as easysetup

easysetup.setup('mypackage', argv = sys.argv)
```

Your package is now installable using `pip` et. al. that support the Python package`setup.py` script convention, i.e.:

```sh
pip install .
```


## Easy package load paths

In any package source file:

```python
# e.g. `~/dev/projects/mypackage/foo/foo.py`

def hello:
    print('hello!')

```

In any other package source file:

```python
# e.g. `~/dev/projects/mypackage/bar/bar.py`

from easypackage import syspath as easysyspath

# add `~/dev/projects/mypackage` to Python system path unless already added
easysyspath.syspath()

from mypackage.utils.foo import foo

foo.hello()

```

And so on.


## Easy package tag/release (WIP/TBA)

In file `release.py` in package project root:

```python
from easypackage import release as easyrelease

easyrelease.release()
```

To tag/release a new version to Git, simply add/update a valid **semver** version tag in `package.json` - according to **Node.js** specification - and then run `python release.py`.

Currently not submitted to any Python package register, but will probably be added soon.


## License

Released under the MIT license.
