from sqlalchemy.dialects.postgresql.base import ischema_names, PGTypeCompiler, ARRAY
from sqlalchemy import types as sqltypes
from sqlalchemy.sql import expression

class LTREE(sqltypes.Concatenable, sqltypes.TypeEngine):
    """Postgresql LTREE type.

    The LTREE datatype can be used for representing labels of data stored in
    hierarchial tree-like structure. For more detailed information please refer
    to http://www.postgresql.org/docs/9.1/static/ltree.html.

    .. note::

        Using :class:`LTREE`, :class:`LQUERY` and :class:`LTXTQUERY` types may
        require installation of Postgresql ltree extension on the server side.
        Please visit http://www.postgres.org for details.
    """

    class Comparator(sqltypes.Concatenable.Comparator):

        def ancestor_of(self, other):
            if isinstance(other, list):
                return self.op('@>')(expression.cast(other, ARRAY(LTREE)))
            else:
                return self.op('@>')(other)

        def descendant_of(self, other):
            if isinstance(other, list):
                return self.op('<@')(expression.cast(other, ARRAY(LTREE)))
            else:
                return self.op('<@')(other)

        def lquery(self, other):
            if isinstance(other, list):
                return self.op('?')(expression.cast(other, ARRAY(LQUERY)))
            else:
                return self.op('~')(other)

        def ltxtquery(self, other):
            return self.op('@')(other)

    comparator_factory = Comparator

    __visit_name__ = 'LTREE'


class LQUERY(sqltypes.TypeEngine):
    """Postresql LQUERY type.

    See :class:`LTREE` for details.
    """
    __visit_name__ = 'LQUERY'


class LTXTQUERY(sqltypes.TypeEngine):
    """Postresql LTXTQUERY type.

    See :class:`LTREE` for details.
    """
    __visit_name__ = 'LTXTQUERY'

ischema_names['ltree'] = LTREE
ischema_names['lquery'] = LQUERY
ischema_names['ltxtquery'] = LTXTQUERY

PGTypeCompiler.visit_LTREE = lambda self, type_: 'LTREE'
PGTypeCompiler.visit_LQUERY = lambda self, type_: 'LQUERY'
PGTypeCompiler.visit_LTXTQUERY = lambda self, type_: 'LTXTQUERY'