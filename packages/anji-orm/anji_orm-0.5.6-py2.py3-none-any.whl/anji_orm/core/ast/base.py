from abc import ABC, abstractmethod
from enum import Enum, auto
import logging
from typing import Set, Any, Optional, Type, TYPE_CHECKING, List, Tuple

from lazy import lazy

from ..utils import prettify_value
from .utils import Interval

if TYPE_CHECKING:
    from ..model import Model  # pylint: disable=unused-import
    from .special import QueryRow, QueryRowOrderMark  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'QueryBiStatement', 'StatementType', 'QueryAndStatement', 'EmptyQueryStatement',
    'QueryAst', 'SamplingType', "QueryBuildException", 'AggregationType',
    'QueryFilterStatement', 'QueryAggregationStatement', 'QueryGroupStatament',
    'QueryChangeStatement'
]

_log = logging.getLogger(__name__)


class QueryBuildException(Exception):

    pass


class StatementType(Enum):

    eq = '=='  # pylint: disable=invalid-name
    lt = '<'  # pylint: disable=invalid-name
    gt = '>'  # pylint: disable=invalid-name
    ne = '!='  # pylint: disable=invalid-name
    le = '<='  # pylint: disable=invalid-name
    ge = '>='  # pylint: disable=invalid-name
    isin = 'in'  # pylint: disable=invalid-name
    bound = 'bound'  # pylint: disable=invalid-name
    match = 'match'  # pylint: disable=invalid-name


class SamplingType(Enum):

    limit = auto()
    skip = auto()
    sample = auto()
    order_by = auto()


class AggregationType(Enum):

    max = auto()
    min = auto()
    sum = auto()
    avg = auto()
    count = auto()


class QueryAst:

    __slots__ = ('_args', 'model_ref')
    _args_order_important = True

    def __init__(self, *args, model_ref=None) -> None:
        self._args = list(args)
        self.model_ref: Optional[Type['Model']] = model_ref

    def _is_same_ordered_args_check(self, other: 'QueryAst') -> bool:
        for index, arg in enumerate(self._args):
            opposite_arg = other._args[index]  # type: ignore
            if opposite_arg.__class__ != arg.__class__:
                return False
            if not isinstance(arg, QueryAst) and arg != opposite_arg:
                return False
            if isinstance(opposite_arg, QueryAst) and not arg.is_same(opposite_arg):
                return False
        return True

    def _is_same_unordered_args_check(self, other: 'QueryAst') -> bool:
        for arg in self._args:
            opposite_arg = None
            if hasattr(arg, 'is_same'):
                opposite_arg = next(filter(arg.is_same, other._args), None)  # pylint: disable=cell-var-from-loop
            else:
                opposite_arg = next(filter(lambda x: arg == x, other._args), None)  # pylint: disable=cell-var-from-loop
            if opposite_arg is None:
                return False
        return True

    def is_same(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if len(self._args) != len(other._args):  # type: ignore
            return False
        if self._args_order_important:
            if not self._is_same_ordered_args_check(other):  # type: ignore
                return False
        else:
            if not self._is_same_unordered_args_check(other):  # type: ignore
                return False
        return True

    def merge(self, _other: 'QueryAst') -> 'QueryAst':
        raise QueryBuildException(f"{self.__class__.__name__} cannot be merged with anything")

    def can_be_merged(self, _other: 'QueryAst') -> bool:  # pylint: disable=no-self-use
        return False

    def implict_cast(self, target_type: Type['QueryAst']) -> Optional['QueryAst']:  # pylint: disable=no-self-use,unused-argument
        return None

    def _adapt_query_args(self) -> None:
        from ..register import orm_register

        for arg in self._args:
            if isinstance(arg, QueryAst):
                arg._adapt_query_args()
        self._args = list(map(orm_register.ensure_compatibility, self._args))

    def changes(self, with_initial: bool = False, with_types: bool = False) -> 'QueryChangeStatement':
        return QueryChangeStatement(
            self, model_ref=self.model_ref, with_initial=with_initial, with_types=with_types
        )

    def build_query(self) -> Any:

        if self.model_ref is None:
            raise QueryBuildException("Cannot build query without model link!")
        self._adapt_query_args()
        return self.model_ref.shared.query_parser.parse_query(self)

    def run(self, without_fetch: bool = False):
        if self.model_ref is None:
            raise QueryBuildException("Cannot build query without model link!")
        return self.model_ref.shared.executor.execute_query(self.build_query(), without_fetch=without_fetch)

    async def async_run(self, without_fetch: bool = False):
        if self.model_ref is None:
            raise QueryBuildException("Cannot build query without model link!")
        return await self.model_ref.shared.executor.execute_query(self.build_query(), without_fetch=without_fetch)


class QueryAggregatableStatement(QueryAst):

    __slots__ = ()

    def max(self, row: 'QueryRow') -> 'QueryAggregationStatement':
        return QueryAggregationStatement(self, row, AggregationType.max, model_ref=self.model_ref)

    def min(self, row: 'QueryRow') -> 'QueryAggregationStatement':
        return QueryAggregationStatement(self, row, AggregationType.min, model_ref=self.model_ref)

    def sum(self, row: 'QueryRow') -> 'QueryAggregationStatement':
        return QueryAggregationStatement(self, row, AggregationType.sum, model_ref=self.model_ref)

    def avg(self, row: 'QueryRow') -> 'QueryAggregationStatement':
        return QueryAggregationStatement(self, row, AggregationType.avg, model_ref=self.model_ref)

    def count(self) -> 'QueryAggregationStatement':
        return QueryAggregationStatement(self, None, AggregationType.count, model_ref=self.model_ref)


class QueryChangeStatement(QueryAst):

    __slots__ = ('with_initial', 'with_types')

    @property
    def base_query(self) -> QueryAst:
        return self._args[0]

    def __init__(
            self, *args, model_ref=None, with_initial: bool = False,
            with_types: bool = False,) -> None:
        super().__init__(*args, model_ref=model_ref)
        self.with_initial = with_initial
        self.with_types = with_types

    def __str__(self) -> str:
        return f"[{str(self.base_query)}].changes()"


class QueryGroupStatament(QueryAggregatableStatement):

    __slots__ = ()

    @property
    def row(self) -> 'QueryRow':
        return self._args[0]

    @property
    def base_query(self) -> 'QueryFilterStatement':
        return self._args[1]

    def __str__(self) -> str:
        return f'{str(self.base_query)}.group({str(self.row)})'


class QueryFilterStatement(QueryAggregatableStatement):

    __slots__ = ('sampling',)

    def __init__(self, *args, model_ref=None) -> None:
        super().__init__(*args, model_ref=model_ref)
        self.sampling: Optional[List[Tuple[SamplingType, Any]]] = None

    def limit(self, limit: int) -> 'QueryFilterStatement':
        if self.sampling is None:
            self.sampling = []
        if any(sample[0] in [SamplingType.sample, SamplingType.limit] for sample in self.sampling):
            raise QueryBuildException(
                "You cannot call limit after sample or limit!"
                " Please, all add order condition in first statement"
            )
        self.sampling.append((SamplingType.limit, limit))
        return self

    def skip(self, skip: int) -> 'QueryFilterStatement':
        if self.sampling is None:
            self.sampling = []
        self.sampling.append((SamplingType.skip, skip))
        return self

    def sample(self, sample: int) -> 'QueryFilterStatement':
        if self.sampling is None:
            self.sampling = []
        self.sampling.append((SamplingType.sample, sample))
        return self

    def order_by(self, *order_marks: 'QueryRowOrderMark') -> 'QueryFilterStatement':
        if self.sampling is None:
            self.sampling = []
        if any(sample[0] == SamplingType.order_by for sample in self.sampling):
            raise QueryBuildException(
                "You cannot call order_by twice!"
                " Please, all add order condition in first order_by statement"
            )
        self.sampling.append((SamplingType.order_by, order_marks))
        return self

    def group(self, row: 'QueryRow') -> QueryGroupStatament:
        return QueryGroupStatament(row, self, model_ref=self.model_ref)


class QueryAggregationStatement(QueryAst):

    __slots__ = ()

    @property
    def base_query(self) -> QueryFilterStatement:
        return self._args[0]

    @property
    def row(self) -> 'QueryRow':
        return self._args[1]

    @property
    def aggregation(self) -> AggregationType:
        return self._args[2]

    def __str__(self) -> str:
        return f'{str(self.aggregation)}({str(self.row)}, {str(self.base_query)})'


class QueryBiStatement(QueryFilterStatement, ABC):

    _statement_type: StatementType
    _provide_merge_for: Set[StatementType]

    __slots__ = ()

    @lazy
    def left(self) -> QueryAst:
        return prettify_value(self._args[0])

    @lazy
    def right(self) -> QueryAst:
        return prettify_value(self._args[1])

    @property
    def statement_type(self) -> StatementType:
        return self._statement_type

    def __and__(self, other: QueryAst) -> QueryAst:
        if not isinstance(other, QueryBiStatement):
            other_candidate = other.implict_cast(QueryBiStatement)
            if other_candidate is None:
                raise TypeError(
                    "Currently, cannot apply and for QueryBiStatement"
                    f" with {other.__class__.__name__} query ast class"
                )
            other = other_candidate
        if self.can_be_merged(other):
            return self.merge(other)
        return QueryAndStatement(self, other, model_ref=self.model_ref or other.model_ref)

    def can_be_merged(self, other: QueryAst) -> bool:
        return (
            isinstance(other, QueryBiStatement) and not self.complicated and
            not other.complicated and self.left.row_name == other.left.row_name
        )

    @abstractmethod
    def _merge_provider(self, other: 'QueryBiStatement') -> Optional['QueryBiStatement']:
        pass

    def merge(self, other: 'QueryAst') -> 'QueryAst':
        if not isinstance(other, QueryBiStatement):
            raise TypeError(f"Currently, cannot merge QueryBiStatement with {other.__class__.__name__} query ast class")
        merge_provider_founded = False
        if other.statement_type in self._provide_merge_for:
            merge_result = self._merge_provider(other)
            merge_provider_founded = True
        elif self.statement_type in other._provide_merge_for:
            merge_result = other._merge_provider(self)
            merge_provider_founded = True
        if not merge_provider_founded:
            raise QueryBuildException("Cannot find merge provider!")
        if merge_result is None:
            return EmptyQueryStatement()
        return merge_result

    @property
    def complicated(self) -> bool:
        """
        Check if query statement has QueryRow on both leafs
        """
        return isinstance(self.right, QueryAst)

    def __str__(self) -> str:
        return f"{self.left} {self.statement_type.value} {self.right}"

    def __repr__(self) -> str:
        return str(self)


class EmptyQueryStatement(QueryAst):
    """
    Empty query statement, return on incompatable statements merge
    """

    __slots__ = ()

    def __and__(self, other):
        return self

    @property
    def complicated(self) -> bool:
        return False

    def can_be_merged(self, _other: 'QueryAst') -> bool:
        return True

    def merge(self, _other: 'QueryAst') -> 'QueryAst':
        return self

    def __str__(self) -> str:
        return '(empty set)'

    def __repl__(self) -> str:
        return str(self)


class QueryAndStatement(QueryFilterStatement):

    _args_order_important = False

    __slots__ = ()

    def __and__(self, other: QueryAst) -> QueryAst:

        def statement_filter(statement):
            if isinstance(statement, QueryAst):
                return statement.can_be_merged(other)
            return False

        if not isinstance(other, QueryBiStatement):
            other_candidate = other.implict_cast(QueryBiStatement)
            if other_candidate is None:
                raise TypeError(
                    "Currently, cannot apply and to QueryAndStatement with"
                    f" {other.__class__.__name__} query ast class"
                )
            other = other_candidate

        merge_candidate: Optional[QueryBiStatement] = next(filter(statement_filter, self._args), None)
        if merge_candidate is not None:
            self._args[self._args.index(merge_candidate)] = merge_candidate.merge(other)
        else:
            self._args.append(other)
        return self

    @property
    def complicated(self) -> bool:
        return True

    def __str__(self) -> str:
        return ' & '.join(map(str, self._args))

    def __repl__(self) -> str:
        return self.__str__()


class QueryEqualStatement(QueryBiStatement):

    _statement_type = StatementType.eq
    _args_order_important = False
    _provide_merge_for = {
        StatementType.ne, StatementType.eq, StatementType.bound, StatementType.ge,
        StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    __slots__ = ()

    def _merge_provider(self, other: QueryBiStatement) -> Optional[QueryBiStatement]:
        compitability_check = (
            (other.statement_type == StatementType.eq and other.right == self.right) or
            (other.statement_type in [StatementType.isin, StatementType.bound] and self.right in other.right) or
            (other.statement_type == StatementType.lt and self.right < other.right) or
            (other.statement_type == StatementType.le and self.right <= other.right) or
            (other.statement_type == StatementType.ge and self.right >= other.right) or
            (other.statement_type == StatementType.gt and self.right > other.right) or
            (other.statement_type == StatementType.ne and self.right != other.right)
        )
        return self if compitability_check else None


class QueryGreaterOrEqualStatement(QueryBiStatement):

    __slots__ = ()

    _statement_type = StatementType.ge
    _provide_merge_for = {
        StatementType.ge, StatementType.gt
    }

    def _merge_provider(self, other: QueryBiStatement) -> Optional[QueryBiStatement]:
        if self.right > other.right:
            return self
        return other


class QueryGreaterStatement(QueryBiStatement):

    __slots__ = ()

    _statement_type = StatementType.gt
    _provide_merge_for = {
        StatementType.gt
    }

    def _merge_provider(self, other: QueryBiStatement) -> Optional[QueryBiStatement]:
        if self.right > other.right:
            return self
        return other


class QueryLowerOrEqualStatement(QueryBiStatement):

    __slots__ = ()

    _statement_type = StatementType.le
    _provide_merge_for = {
        StatementType.ge, StatementType.le, StatementType.lt, StatementType.gt
    }

    def _merge_provider(self, other: QueryBiStatement) -> Optional[QueryBiStatement]:
        if other.statement_type in [StatementType.le, StatementType.lt]:
            if self.right < other.right:
                return self
            return other
        if self.right >= other.right:
            return QueryBoundStatement(
                self.left,
                Interval(
                    other.right, self.right,
                    left_close=other.statement_type == StatementType.ge, right_close=True
                ),
                model_ref=self.model_ref or other.model_ref
            )
        return None


class QueryLowerStatement(QueryBiStatement):

    __slots__ = ()

    _statement_type = StatementType.lt
    _provide_merge_for = {
        StatementType.ge, StatementType.lt, StatementType.gt
    }

    def _merge_provider(self, other: QueryBiStatement) -> Optional[QueryBiStatement]:
        if other.statement_type == StatementType.lt:
            if self.right < other.right:
                return self
            return other
        if self.right >= other.right:
            return QueryBoundStatement(
                self.left,
                Interval(
                    other.right, self.right,
                    left_close=other.statement_type == StatementType.ge, right_close=False
                ),
                model_ref=self.model_ref or other.model_ref
            )
        return None


class QueryNotEqualStatement(QueryBiStatement):

    __slots__ = ()

    _statement_type = StatementType.ne
    _args_order_important = False
    _provide_merge_for = {
        StatementType.ne, StatementType.eq, StatementType.bound, StatementType.ge,
        StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBiStatement) -> Optional[QueryBiStatement]:
        compitability_check = (
            (other.statement_type == StatementType.eq and other.right == self.right) or
            (other.statement_type in [StatementType.isin, StatementType.bound] and self.right in other.right) or
            (other.statement_type == StatementType.lt and self.right < other.right) or
            (other.statement_type == StatementType.le and self.right <= other.right) or
            (other.statement_type == StatementType.ge and self.right >= other.right) or
            (other.statement_type == StatementType.gt and self.right > other.right) or
            (other.statement_type == StatementType.ne and self.right != other.right)
        )
        if not compitability_check:
            return other
        elif other.statement_type == StatementType.isin:
            new_elements = tuple(x for x in other.right if x != self.right)
            if new_elements:
                return QueryContainsStatement(self.left, new_elements, model_ref=self.model_ref or other.model_ref)
        elif other.statement_type == StatementType.bound:
            if self.right in other.right:
                _log.warning("Currently, bound statement cannot be merged with ne statement, so just ingore ne statement")
            return other
        return None


class QueryContainsStatement(QueryBiStatement):

    __slots__ = ()

    _statement_type = StatementType.isin
    _provide_merge_for = {
        StatementType.ge, StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBiStatement) -> Optional[QueryBiStatement]:
        if other.statement_type == StatementType.isin:
            intersection = tuple(x for x in self.right if x in other.right)
            if intersection:
                return QueryContainsStatement(self.left, intersection, model_ref=self.model_ref or other.model_ref)
            return None
        method_name = f"__{other.statement_type.name}__"
        for element in self.right:
            if not getattr(element, method_name)(other.right):
                return None
        return self


class QueryBoundStatement(QueryBiStatement):

    __slots__ = ()

    _statement_type = StatementType.bound
    _provide_merge_for = {
        StatementType.bound, StatementType.ge,
        StatementType.le, StatementType.lt, StatementType.gt, StatementType.isin
    }

    def _merge_provider(self, other: QueryBiStatement) -> Optional[QueryBiStatement]:
        if other.statement_type == StatementType.isin:
            for element in other.right:
                if element not in self.right:
                    return None
            return other
        interval = self.right.clone()
        # Convert to QueryBoundStatement to make same codebase for many statement type
        # If you want to change it, make sure that all types covered
        if other.statement_type in [StatementType.le, StatementType.lt]:
            interval.right_close = other.statement_type == StatementType.le
            interval.right_bound = other.right
            other = QueryBoundStatement(self.left, interval, model_ref=self.model_ref or other.model_ref)
        if other.statement_type in [StatementType.ge, StatementType.gt]:
            interval.left_close = other.statement_type == StatementType.ge
            interval.left_bound = other.right
            other = QueryBoundStatement(self.left, interval, model_ref=self.model_ref or other.model_ref)
        if other.statement_type == StatementType.bound:
            interval = other.right
        if interval.valid:
            if self.right.contains_interval(interval):
                return other
            if interval.contains_interval(self.right):
                return self
        return None


class QueryMatchStatement(QueryBiStatement):

    __slots__ = ()

    _statement_type: StatementType = StatementType.match
    _provide_merge_for: Set[StatementType] = set()

    def can_be_merged(self, other: QueryAst) -> bool:
        return False

    def _merge_provider(self, other: 'QueryBiStatement') -> Optional['QueryBiStatement']:
        raise QueryBuildException("Merge cannot be provided for complicated match statement")
