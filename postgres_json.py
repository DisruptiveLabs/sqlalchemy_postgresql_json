import collections

from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql.base import ischema_names, PGTypeCompiler
from sqlalchemy import types as sqltypes
from sqlalchemy.sql import functions as sqlfunc
from sqlalchemy.sql.operators import custom_op
from sqlalchemy import util


# simplejson is faster at loading, json is faster at dumping. lets use the
# best of both worlds
from json import dumps as dumpjson

from sqlalchemy.ext.mutable import MutableDict, Mutable


__all__ = ['JSON', 'json']

#This requires the use of psycopg2 and postgresql afaik, it probably wont work with zxJDBC, and definitely won't with
# py-postgresql or pg8000, but why would you use those anyway?


class JSON(sqltypes.Concatenable, sqltypes.TypeEngine):
    """Represents the Postgresql JSON type.

    The :class:`.JSON` type stores python dictionaries using standard
    python json libraries to parse and serialize the data for storage
    in your database.
    """

    __visit_name__ = 'JSON'

    class comparator_factory(sqltypes.Concatenable.Comparator):

        def __getitem__(self, other):
            '''Gets the value at a given index for an array.'''
            return self.expr.op('->>')(other)

        def get_array_item(self, other):
            return self.expr.op('->')(other)

        def _adapt_expression(self, op, other_comparator):
            if isinstance(op, custom_op):
                if op.opstring in ['->', '#>']:
                    return op, sqltypes.Boolean
                elif op.opstring in ['->>', '#>>']:
                    return op, sqltypes.String
            return sqltypes.Concatenable.Comparator. \
                _adapt_expression(self, op, other_comparator)

    def bind_processor(self, dialect):
        if util.py2k:
            encoding = dialect.encoding

        def process(value):
            if value is not None:
                return dumpjson(value)
            return value

        return process

    def result_processor(self, dialect, coltype):
        return lambda v: v


ischema_names['json'] = JSON


class json(sqlfunc.GenericFunction):
    type = JSON
    name = 'to_json'


class _JSONFunction(sqlfunc.GenericFunction):
    type = sqltypes.Integer
    name = 'json_array_length'


class _JSONExtractPathFunction(sqlfunc.GenericFunction):
    type = JSON
    name = 'json_extract_path'


class _JSONExtractPathTestFunction(sqlfunc.GenericFunction):
    type = sqltypes.String
    name = 'json_extract_path_test'


PGTypeCompiler.visit_JSON = lambda self, type_: 'JSON'


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
            return Mutable.coerce(key, value)
        else:
            return value


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


MutableList.associate_with(postgresql.ARRAY)
JSONMutableDict.associate_with(JSON)