
# =========================================
#       DEPS
# --------------------------------------

import sys
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

from easypackage.utils.banner import banner


# =========================================
#       CLASSES
# --------------------------------------

class AttributeDict(dict):

    """
    A class to convert a nested Dictionary into an object with key-values
    accessibly using attribute notation (AttributeDict.attribute) instead of
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to recurse down nested dicts (like: AttributeDict.attr.attr)

    @see https://github.com/databio/pypiper/blob/master/pypiper/AttributeDict.py
    @see https://stackoverflow.com/questions/2390827/how-to-properly-subclass-dict-and-override-getitem-setitem (enhancements)
    """

    def __init__(self, entries, default = False):
        """
        :param entries: A dictionary (key-value pairs) to add as attributes.
        :param default: Should this AttributeDict object return Default
        values for attributes that it does not have? If True, then
        AttributeDict.java would return "java" instead of raising an error,
        if no .java attribute were found.
        """
        dict.__init__(self, entries)

        self.add_entries(entries, default)

    def add_entries(self, entries, default = False):
        for key, value in entries.items():
            if type(value) is dict:
                self.__dict__[key] = AttributeDict(value, default)

            else:
                try:
                    # try expandvars() to allow the yaml to use
                    # shell variables.
                    self.__dict__[key] = path.expandvars(value) # value

                except TypeError:
                    # if value is an int, expandvars() will fail; if
                    # expandvars() fails, just use the raw value
                    self.__dict__[key] = value

    def get(self, key, default = None):
        return self.__getattr__(key) or default

    def keys(self, *args, **kwargs):
        return self.__dict__.keys(*args, **kwargs)

    def items(self, *args, **kwargs):
        return self.__dict__.items(*args, **kwargs)

    def iteritems(self, *args, **kwargs):
        return self.__dict__.iteritems(*args, **kwargs)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v

    # __*item__

    def __getitem__(self, key):
        """
        Provides `dict` style property access to dictionary key-values.

        @example:

            value = object['key']

        """
        return getattr(self, key)

    def __setitem__(self, key, value):
        """
        Provides `dict` style property assignment to dictionary key-values.

        @example:

            object['key'] = value

        """
        setattr(self, key, value)

    def __delitem__(self, key):
        """
        Provides `dict` style property deletion to dictionary key-values.

        @example:

            del object['key']

        """
        setattr(self, key, value)

     # __*attr__

    def __getattr__(self, key):
        """
        Provides `object` style attribute access to dictionary key-values.

        @example:

            value = object.key

        """
        return self.__dict__.get(key, None)

    def __setattr__(self, key, value):
        """
        Provides `object` style attribute assignment to dictionary key-values.

        @example:

            object.key = value

        """
        self.__dict__[key] = value

    def __delattr__(self, key):
        """
        Provides `object` style attribute deletion to dictionary key-values.

        @example:

            del object.key

        """
        del self[key]

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return repr(self.__dict__)

    def __dir__(self):
        return dir(type(self)) + list(self.keys())


# =========================================
#       MAIN
# --------------------------------------

if __name__ == '__main__':

    with banner(__file__):
        data = {
            'a': {
                'b': {
                    'c': [1, 2, 3]
                }
            }
        }

        object = AttributeDict(data)

        print('object = AttributeDict({0})\n'.format(data))

        print('object\n\n\t{0}\n'.format(object))
        print('object.a\n\n\t{0}\n'.format(object.a))
        print('object.a.b\n\n\t{0}\n'.format(object.a.b))
        print('object.a.b.c\n\n\t{0}\n'.format(object.a.b.c))
