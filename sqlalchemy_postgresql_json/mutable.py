from __future__ import absolute_import

import collections
from sqlalchemy.ext.mutable import MutableDict, Mutable
from sqlalchemy_postgresql_json.pgjson import JSON
from sqlalchemy.dialects import postgresql

class JSONMutableDict(MutableDict):
    def __setitem__(self, key, value):
        if isinstance(value, collections.Mapping):
            if not isinstance(value, JSONMutableDict):
                value = JSONMutableDict.coerce(key, value)
        elif isinstance(value, (set, list, tuple)):
            if not isinstance(value, JSONMutableList):
                value = JSONMutableList.coerce(key, value)
        dict.__setitem__(self, key, value)
        self.changed()

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        if isinstance(value, dict):
            if not isinstance(value, JSONMutableDict):
                value = JSONMutableDict.coerce(key, value)
                value._parents = self._parents
                dict.__setitem__(self, key, value)
        elif isinstance(value, (set, list, tuple)):
            if not isinstance(value, JSONMutableList):
                value = JSONMutableList.coerce(key, value)
                value._parents = self._parents
                dict.__setitem__(self, key, value)
        return value

    @classmethod
    def coerce(cls, key, value):
        """Convert plain dictionary to JSONMutableDict."""
        if not isinstance(value, JSONMutableDict):
            if isinstance(value, dict):
                return JSONMutableDict(value)
            if isinstance(value, (list, tuple, set)):
                return JSONMutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def update(self, *args, **kwargs):
        super(MutableDict, self).update(*args, **kwargs)
        self.changed()



class MutableList(Mutable, list):
    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.changed()

    def __setslice__(self, i, j, sequence):
        list.__setslice__(self, i, j, sequence)
        self.changed()

    def __delslice__(self, i, j):
        list.__delslice__(self, i, j)
        self.changed()

    def extend(self, iterable):
        list.extend(self, iterable)
        self.changed()

    def insert(self, index, p_object):
        list.insert(self, index, p_object)
        self.changed()

    def append(self, p_object):
        list.append(self, p_object)
        self.changed()

    def pop(self, index=None):
        list.pop(self, index)
        self.changed()

    def remove(self, value):
        list.remove(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, (set, list, tuple)):
                return MutableList(value)
            return Mutable.coerce(key, value)
        return value

    def __getstate__(self):
        return list(self)
    
    def __setstate__(self, state):
        for i in state:
            self.append(i)


class JSONMutableList(MutableList):
    def __setitem__(self, key, value):
        if isinstance(value, collections.Mapping):
            if not isinstance(value, JSONMutableDict):
                value = JSONMutableDict(value)
        elif isinstance(value, (set, list, tuple)):
            if not isinstance(value, JSONMutableList):
                value = JSONMutableList(value)
        list.__setitem__(self, key, value)
        self.changed()

    def __getitem__(self, key):
        value = super(JSONMutableList, self).__getitem__(key)
        if isinstance(value, collections.Mapping):
            if not isinstance(value, JSONMutableDict):
                value = JSONMutableDict.coerce(key, value)
                value._parents = self._parents
                list.__setitem__(self, key, value)
        elif isinstance(value, (set, list, tuple)):
            if not isinstance(value, JSONMutableList):
                value = JSONMutableList.coerce(key, value)
                value._parents = self._parents
                list.__setitem__(self, key, value)
        return value

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, JSONMutableList):
            if isinstance(value, (set, list, tuple)):
                return JSONMutableList(value)
            return Mutable.coerce(key, value)
        return value

def monkey_patch_array():
    MutableList.associate_with(postgresql.ARRAY)

def monkey_patch_json():
    JSONMutableDict.associate_with(JSON)

def monkey_patch_all():
    monkey_patch_array()
    monkey_patch_json()

__all__ = ['monkey_patch_array',
           'monkey_patch_json',
           'monkey_patch_all',
           'JSONMutableDict',
           'JSONMutableList',
           'MutableList',
           'MutableDict']
