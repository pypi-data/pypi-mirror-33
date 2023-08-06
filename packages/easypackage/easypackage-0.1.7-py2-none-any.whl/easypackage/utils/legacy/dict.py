

# =========================================
#       DEPS
# --------------------------------------

import sys
import six

from os import path

CURRENT_PATH = path.abspath(path.dirname(__file__))
ROOT_PATH = path.abspath(path.join(CURRENT_PATH, '..', '..', '..'))

try:
    try:
        sys.path.remove(CURRENT_PATH)
    except:
        pass

    sys.path.index(ROOT_PATH)

except ValueError:
    sys.path.insert(0, ROOT_PATH)

PYTHON_VERSION = sys.version_info[0]


# =========================================
#       FUNCTIONS
# --------------------------------------

def bytes2str(data):
    if six.PY2:
        return data

    if isinstance(data, bytes):
        # print('bytes', data)
        return data.decode()

    if isinstance(data, str):
        # print('str', data)
        return str(data)

    if isinstance(data, dict):
        # print('dict', data)
        return dict(map(bytes2str, data.items()))

    if isinstance(data, tuple):
        # print('tuple', data)
        return tuple(map(bytes2str, data))

    if isinstance(data, list):
        # print('list', data)
        return list(map(bytes2str, data))

    if isinstance(data, set):
        # print('set', data)
        return set(map(bytes2str, data))

    return data


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':

    with Banner(__file__):
        pass
