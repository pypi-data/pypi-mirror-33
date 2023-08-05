import abc
from typing import Type, TypeVar, Generic, List, Callable, TYPE_CHECKING, Tuple, Optional
from functools import partial
from random import choices

from toolz.functoolz import compose
from toolz.itertoolz import groupby

from .ast import (
    QueryAst, QueryBiStatement, EmptyQueryStatement, QueryTable, QueryAndStatement,
    QueryBuildException, SamplingType, AggregationType, QueryFilterStatement,
    QueryAggregationStatement, QueryRow, QueryGroupStatament,
    QueryChangeStatement
)
from .loggers import abstraction_emulation_log

if TYPE_CHECKING:
    from .model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.6"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['AbstractQueryParser', 'BaseQueryParser']

T = TypeVar('T')
SAMPLING_CANDIDATE = 5


def query_bi_statement_constrains(statement: QueryAst) -> QueryAst:
    if not isinstance(statement, QueryBiStatement):
        raise QueryBuildException("Unsupported query ast type here")
    return statement


class AbstractQueryParser(Generic[T]):

    @abc.abstractmethod
    def parse_query(self, query: QueryAst) -> T:
        pass


class BaseQueryParser(AbstractQueryParser[T]):  # pylint: disable=too-many-public-methods

    __index_selection__: bool = False
    __sample_emulation__: bool = False
    __processing_hook_support__: bool = False
    __target_database__: str

    @abc.abstractmethod
    def build_empty_query(self, db_query: T) -> T:
        pass

    @abc.abstractmethod
    def initial_query(self, model_class: Type['Model'], query: QueryAst) -> T:
        pass

    @abc.abstractmethod
    def build_table_query(self, db_query: T, model_class: Type['Model']) -> T:
        pass

    @abc.abstractmethod
    def process_simple_statement(self, db_query: T, simple_statement: QueryBiStatement) -> T:
        pass

    @abc.abstractmethod
    def process_complicated_statement(self, search_query: T, statement: QueryBiStatement) -> T:
        pass

    @abc.abstractmethod
    def process_sampling_statement(self, db_query: T, sampling_type: SamplingType, sampling_arg) -> T:
        pass

    @abc.abstractmethod
    def process_aggregation_statement(
            self, db_query: T, aggregation_type: AggregationType,
            row: QueryRow) -> T:
        pass

    @abc.abstractmethod
    def process_group_statement(self, db_query: T, group_row: QueryRow) -> T:
        pass

    @abc.abstractmethod
    def process_change_statement(self, db_query: T, change_statement: QueryChangeStatement) -> T:
        pass

    def complicated_statement_filter(self, statement: QueryBiStatement) -> bool:  # pylint: disable=no-self-use
        return statement.complicated

    def add_post_processing_hook(self, _db_query: T, _hook: Callable) -> T:  # pylint: disable=no-self-use
        raise QueryBuildException("Cannot use processing hook!")

    def add_pre_processing_hook(self, _db_query: T, _hook: Callable) -> T:  # pylint: disable=no-self-use
        raise QueryBuildException("Cannot use processing hook!")

    def secondary_indexes_query(  # pylint: disable=no-self-use
            self, _search_query: T,
            _indexed_statements: List[QueryBiStatement], _selected_index: str) -> T:
        raise QueryBuildException("Cannot process secondary index selection!")

    def query_pre_processing(self, query: QueryAst) -> QueryAst:  # pylint: disable=no-self-use
        return query

    def query_post_processing(self, db_query: T, _model_class: Type['Model']) -> T:  # pylint: disable=no-self-use
        return db_query

    def parse_filter_query(self, search_query: T, query: QueryFilterStatement, model_class: Type['Model']) -> T:
        if isinstance(query, QueryTable):
            search_query = self.build_table_query(search_query, model_class)
        else:
            simple_statements, complicated_statements = self.split_query(query)
            if simple_statements:
                search_query = self.process_simple_statements(
                    model_class, search_query, simple_statements
                )
            if complicated_statements:
                search_query = self.process_complicated_statements(search_query, complicated_statements)
        return self.process_sampling_statements(query, search_query)

    def parse_query_without_processing(self, search_query: T, query: QueryAst, model_class: Type['Model']) -> T:
        if isinstance(query, EmptyQueryStatement):
            search_query = self.build_empty_query(search_query)
        elif isinstance(query, QueryAggregationStatement):
            search_query = self.process_aggregation_statement(
                self.parse_query_without_processing(search_query, query.base_query, model_class),
                query.aggregation, query.row
            )
        elif isinstance(query, QueryGroupStatament):
            search_query = self.process_group_statement(
                self.parse_query_without_processing(search_query, query.base_query, model_class),
                query.row
            )
        elif isinstance(query, QueryChangeStatement):
            search_query = self.process_change_statement(
                self.parse_query_without_processing(search_query, query.base_query, model_class),
                query
            )
        elif isinstance(query, QueryFilterStatement):
            search_query = self.parse_filter_query(search_query, query, model_class)
        else:
            raise QueryBuildException("Cannot parse %s" % query)
        return search_query

    def parse_query(self, query: QueryAst) -> T:
        model_class: Optional[Type['Model']] = query.model_ref
        if model_class is None:
            raise QueryBuildException("Cannot parse query without model ref")
        query = self.query_pre_processing(query)
        search_query = self.initial_query(model_class, query)
        search_query = self.parse_query_without_processing(search_query, query, model_class)
        return self.query_post_processing(search_query, model_class)

    def split_query(self, query: QueryAst) -> Tuple[List[QueryBiStatement], List[QueryBiStatement]]:  # pylint: disable=no-self-use
        if not isinstance(query, QueryAndStatement):
            if not isinstance(query, QueryBiStatement):
                raise QueryBuildException("Unsupported query ast type here")
            if self.complicated_statement_filter(query):
                return [], [query]
            return [query], []
        groupby_result = groupby(
            compose(self.complicated_statement_filter, query_bi_statement_constrains),
            query._args
        )
        simple_statements: List[QueryBiStatement] = groupby_result.get(False, [])
        complicated_statements: List[QueryBiStatement] = groupby_result.get(True, [])
        return simple_statements, complicated_statements

    def process_simple_statements(
            self, model_class: Type['Model'], search_query: T, simple_statements: List[QueryBiStatement]) -> T:
        if self.__index_selection__:
            indexed_statements: List[QueryBiStatement] = []
            not_indexed_statements: List[QueryBiStatement] = []
            for statement in simple_statements:
                field_name = statement.left.row_name
                if field_name in model_class._fields and model_class._fields[field_name].secondary_index:
                    indexed_statements.append(statement)
                else:
                    not_indexed_statements.append(statement)
            if indexed_statements:
                selected_index, unused_fields = model_class._index_policy.value.select_secondary_index(
                    model_class, [x.left.row_name for x in indexed_statements]
                )
                if unused_fields:
                    not_indexed_statements.extend([x for x in indexed_statements if x.left.row_name in unused_fields])
                search_query = self.secondary_indexes_query(
                    search_query, [x for x in indexed_statements if x.left.row_name in selected_index], selected_index
                )
            for simple_statement in not_indexed_statements:
                search_query = self.process_simple_statement(search_query, simple_statement)
        else:
            for simple_statement in simple_statements:
                search_query = self.process_simple_statement(search_query, simple_statement)
        return search_query

    def process_complicated_statements(
            self, search_query: T, complicated_statements: List[QueryBiStatement]) -> T:
        for statement in complicated_statements:
            search_query = self.process_complicated_statement(search_query, statement)
        return search_query

    def process_sampling_statements(self, query: QueryFilterStatement, db_query: T) -> T:
        was_limited_already = False
        if query.sampling:
            for sampling_type, sampling_arg in query.sampling:
                if sampling_type == SamplingType.sample:
                    if self.__sample_emulation__:
                        db_query = self._sampling_simulation(db_query, sampling_arg, was_limited_already)
                    else:
                        db_query = self.process_sampling_statement(db_query, sampling_type, sampling_arg)
                else:
                    if sampling_type == SamplingType.limit:
                        was_limited_already = True
                    db_query = self.process_sampling_statement(db_query, sampling_type, sampling_arg)
        return db_query

    def _sampling_simulation(self, db_query: T, sample_count: int, was_limited_already: bool) -> T:
        abstraction_emulation_log.info('%s not support sampling, to, sampling will be emulated', self.__target_database__)
        if not was_limited_already:
            db_query = self.process_sampling_statement(db_query, SamplingType.limit, SAMPLING_CANDIDATE * sample_count)
        db_query = self.add_post_processing_hook(db_query, compose(partial(choices, k=sample_count), list))
        return db_query
