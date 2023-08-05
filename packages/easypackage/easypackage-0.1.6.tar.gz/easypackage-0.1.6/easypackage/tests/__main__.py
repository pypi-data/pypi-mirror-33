
# =========================================
#       DEPS
# --------------------------------------

import sys

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


# =========================================
#       RUN
# --------------------------------------

suite = helper.suite(CURRENT_PATH)

helper.run(suite)
