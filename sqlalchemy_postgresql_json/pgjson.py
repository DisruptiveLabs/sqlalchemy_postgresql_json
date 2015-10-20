from __future__ import absolute_import

from sqlalchemy.dialects.postgresql.base import ischema_names, PGTypeCompiler
from sqlalchemy import types as sqltypes
from sqlalchemy.sql import functions as sqlfunc
from sqlalchemy.sql.operators import custom_op
from sqlalchemy import util

from psycopg2._json import register_default_json
from functools import partial
from datetime import datetime
import json as _json, sys

try:
    import cdecimal as decimal
    sys.modules['decimal'] = decimal
except ImportError:
    import decimal

#This requires the use of psycopg2 for PostgreSQL, as it specifically registers a custom json
# converter for psycopg2 to be able to encode and decode Decimals and DateTimes

def to_json(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return {'__class__': 'datetime',
                '__value__': obj.isoformat()}
    raise TypeError(repr(obj) + ' is not JSON serializable')

def from_json(obj):
    if '__class__' in obj:
        type = obj.get('__class__')
        if type == 'Decimal':
            return float(obj.get('__value__'))
        elif type == 'datetime':
            return datetime.strptime(obj.get('__value__'), '%Y-%m-%dT%H:%M:%S.%fZ')
    return obj

_loads = partial(_json.loads, object_hook=to_json)
_dumps = partial(_json.dumps, default=from_json)

register_default_json(loads=partial(_json.loads, object_hook=from_json))

def register_json(loads=None, dumps=None):
    if loads:
        globals()['_loads'] = loads
        register_default_json(loads=loads)
    if dumps:
        globals()['_dumps'] = dumps

class JSON(sqltypes.Concatenable, sqltypes.TypeEngine):
    """Represents the PostgreSQL JSON type.

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
                return _dumps(value)
            return value

        return process

    def result_processor(self, dialect, coltype):
        #psycopg2 handles this for us, kinda thankfully
        return lambda v: v

ischema_names['json'] = JSON


class json(sqlfunc.GenericFunction):
    type = JSON
    name = 'to_json'

def visit_JSON(self, type_, **kw):
    return 'JSON'

PGTypeCompiler.visit_JSON = visit_JSON

__all__ = ['JSON', 'json', 'register_json']
