
# =========================================
#       DEPS
# --------------------------------------

import sys

from os import path

CURRENT_PATH = path.abspath(path.dirname(__file__))
ROOT_PATH = path.abspath(path.join(CURRENT_PATH, '..'))

try:
    sys.path.index(ROOT_PATH)
except ValueError:
    sys.path.append(ROOT_PATH)

import easypackage.__errors__ as __errors__

# import easypackage.release as release
# import easypackage.root as root
# import easypackage.setup as setup
# import easypackage.syspath as syspath

# import __errors__

# import release
# import root
# import setup
# import syspath
