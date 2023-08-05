from typing import Type, Optional, List

from .base import (
    QueryAst, QueryContainsStatement, QueryEqualStatement, QueryGreaterStatement,
    QueryGreaterOrEqualStatement, QueryNotEqualStatement, QueryLowerStatement,
    QueryLowerOrEqualStatement, QueryBiStatement, QueryAndStatement, QueryFilterStatement,
    QueryMatchStatement
)

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["QueryRow", "BooleanQueryRow", "QueryTable", "DictQueryRow", "QueryRowOrderMark"]


class QueryTable(QueryFilterStatement):

    __slots__ = ()

    @property
    def table_name(self):
        return self._args[0]

    def __str__(self) -> str:
        return f'table[{self.table_name}]'


class QueryRow(QueryAst):

    __slots__ = ()

    @property
    def row_name(self):
        return self._args[0]

    @property
    def row_path(self):
        return [self._args[0]]

    @property
    def secondary_index(self):
        return self._args[1]

    @property
    def amount(self):
        return QueryRowOrderMark(self)

    def one_of(self, *variants) -> QueryBiStatement:
        return QueryContainsStatement(self, variants, model_ref=self.model_ref)

    def contains(self, another_row: 'QueryRow') -> QueryBiStatement:
        return QueryContainsStatement(another_row, self, model_ref=self.model_ref)

    def match(self, other) -> QueryBiStatement:
        return QueryMatchStatement(self, other, model_ref=self.model_ref)

    def __eq__(self, other) -> QueryBiStatement:  # type: ignore
        return QueryEqualStatement(self, other, model_ref=self.model_ref)

    def eq(self, other) -> QueryBiStatement:  # pylint: disable=invalid-name
        return QueryEqualStatement(self, other, model_ref=self.model_ref)

    def __ge__(self, other) -> QueryBiStatement:
        return QueryGreaterOrEqualStatement(self, other, model_ref=self.model_ref)

    def ge(self, other) -> QueryBiStatement:  # pylint: disable=invalid-name
        return QueryGreaterOrEqualStatement(self, other, model_ref=self.model_ref)

    def __gt__(self, other) -> QueryBiStatement:
        return QueryGreaterStatement(self, other, model_ref=self.model_ref)

    def gt(self, other) -> QueryBiStatement:  # pylint: disable=invalid-name
        return QueryGreaterStatement(self, other, model_ref=self.model_ref)

    def __ne__(self, other) -> QueryBiStatement:  # type: ignore
        return QueryNotEqualStatement(self, other, model_ref=self.model_ref)

    def ne(self, other) -> QueryBiStatement:  # pylint: disable=invalid-name
        return QueryNotEqualStatement(self, other, model_ref=self.model_ref)

    def __lt__(self, other) -> QueryBiStatement:
        return QueryLowerStatement(self, other, model_ref=self.model_ref)

    def lt(self, other) -> QueryBiStatement:  # pylint: disable=invalid-name
        return QueryLowerStatement(self, other, model_ref=self.model_ref)

    def __le__(self, other) -> QueryBiStatement:
        return QueryLowerOrEqualStatement(self, other, model_ref=self.model_ref)

    def le(self, other) -> QueryBiStatement:  # pylint: disable=invalid-name
        return QueryLowerOrEqualStatement(self, other, model_ref=self.model_ref)

    def __str__(self) -> str:
        return f"row[{self._args[0]}]"


class QueryRowOrderMark:

    __slots__ = ('row', 'order')

    def __init__(self, query_row: QueryRow) -> None:
        self.row = query_row
        self.order = 'asc'

    def desc(self) -> 'QueryRowOrderMark':
        self.order = 'desc'
        return self

    def asc(self) -> 'QueryRowOrderMark':
        self.order = 'asc'
        return self

    @property
    def row_name(self):
        return self.row.row_name

    @property
    def row_path(self):
        return self.row.row_path

    @property
    def secondary_index(self):
        return self.row.secondary_index


class BooleanQueryRow(QueryRow):

    __slots__ = ()

    def false(self) -> QueryBiStatement:
        return QueryEqualStatement(self, False, model_ref=self.model_ref)

    def true(self) -> QueryBiStatement:
        return QueryEqualStatement(self, True, model_ref=self.model_ref)

    def __invert__(self) -> QueryBiStatement:
        return self.false()

    def implict_cast(self, target_type: Type['QueryAst']) -> Optional['QueryAst']:
        if target_type == QueryBiStatement:
            return QueryEqualStatement(self, True, model_ref=self.model_ref)
        return None

    def __and__(self, other) -> QueryAndStatement:
        return QueryAndStatement(
            QueryEqualStatement(self, True, model_ref=self.model_ref),
            other,
            model_ref=self.model_ref
        )


class DictQueryRow(QueryRow):

    __slots__ = ()

    @property
    def row_name(self) -> str:
        return '.'.join(self._args)

    @property
    def secondary_index(self):
        return False

    @property
    def row_path(self) -> List[str]:
        return self._args

    def __getattr__(self, name) -> 'DictQueryRow':
        return DictQueryRow(*(self._args + [name]), model_ref=self.model_ref)

    def __getitem__(self, name) -> 'DictQueryRow':
        return DictQueryRow(*(self._args + [name]), model_ref=self.model_ref)

    def __str__(self) -> str:
        return f"row[{self.row_name}]"
