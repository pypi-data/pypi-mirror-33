# pylint: disable=no-self-use
from datetime import datetime
from typing import Type, Callable
import operator

from ...core import (
    QueryBinaryFilterStatement, StatementType, Interval,
    QueryBuildException, SamplingType, Model, abstraction_ignore_log,
    QueryRowOrderMark, BaseFilterQueryParser
)

from ..lib import (
    AbstractCouchDBQuery, CouchDBMangoQuery
)
from ..utils import serialize_datetime

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.8"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['CouchDBFilterQueryParser']


STATEMENT_MAPPING = {
    StatementType.eq: "$eq",
    StatementType.ne: "$ne",
    StatementType.le: "$lte",
    StatementType.ge: "$gte",
    StatementType.lt: "$lt",
    StatementType.gt: "$gt",
    StatementType.match: "$regex"
}

SAMPLING_CANDIDATE = 5


def _ensure_query_arg_compitability(value):
    if isinstance(value, datetime):
        return serialize_datetime(value)
    return value


_itemgetter_rows = operator.itemgetter("rows")  # pylint: disable=invalid-name
_itemgetter_doc = operator.itemgetter("doc")  # pylint: disable=invalid-name


class CouchDBFilterQueryParser(BaseFilterQueryParser[AbstractCouchDBQuery]):

    __index_selection__ = False
    __sample_emulation__ = True
    __processing_hook_support__ = True
    __target_database__ = 'CouchDB'

    def build_empty_query(self, _db_query: AbstractCouchDBQuery) -> AbstractCouchDBQuery:
        return CouchDBMangoQuery({}, '')

    def build_table_query(self, db_query: AbstractCouchDBQuery, _model_class: Type[Model]) -> AbstractCouchDBQuery:
        db_query = db_query.to_mango_query()
        db_query.selector = {"_id": {"$gt": None}}
        return db_query

    def process_simple_statement(self, db_query: AbstractCouchDBQuery, simple_statement: QueryBinaryFilterStatement) -> AbstractCouchDBQuery:
        row_name = simple_statement.left.row_name
        db_query = db_query.to_mango_query()
        row_query_dict = db_query.selector.setdefault(row_name, {})
        if simple_statement.statement_type == StatementType.isin:
            row_query_dict['$in'] = _ensure_query_arg_compitability(simple_statement.right)
        elif simple_statement.statement_type == StatementType.bound:
            interval: Interval = simple_statement.right
            right_bound_key = "$lte" if interval.right_close else "$lt"
            left_bound_key = "$gte" if interval.left_close else "$gt"
            row_query_dict[left_bound_key] = _ensure_query_arg_compitability(interval.left_bound)
            row_query_dict[right_bound_key] = _ensure_query_arg_compitability(interval.right_bound)
        else:
            db_query.selector[row_name] = {
                STATEMENT_MAPPING[simple_statement.statement_type]: _ensure_query_arg_compitability(simple_statement.right)
            }
        return db_query

    def process_complicated_statement(self, db_query: AbstractCouchDBQuery, statement: QueryBinaryFilterStatement) -> AbstractCouchDBQuery:
        db_query = db_query.to_ddoc_view()
        db_query.ddoc_view.map_function.add(statement)
        return db_query

    def process_sampling_statement(self, db_query: AbstractCouchDBQuery, sampling_type: SamplingType, sampling_arg) -> AbstractCouchDBQuery:
        if sampling_type == SamplingType.order_by:
            db_query.sort = []
            general_direction = None
            order_mark: QueryRowOrderMark
            for order_mark in sampling_arg:
                if general_direction is None:
                    general_direction = order_mark.order
                if general_direction == order_mark.order:
                    db_query.sort.append(order_mark.row_name)
                else:
                    abstraction_ignore_log.warning(
                        "CouchDB cannot sort in multi direction, so"
                        " sorting by %s in %s order was ignored",
                        order_mark.row_name, order_mark.order
                    )
            if general_direction != 'asc':
                db_query.sort = [{x: 'desc'} for x in db_query.sort]
        else:
            if getattr(db_query, sampling_type.name, None) is not None:
                raise QueryBuildException(f"Cannot use {sampling_type.name} sampling two times!")
            setattr(db_query, sampling_type.name, sampling_arg)
        return db_query

    def add_post_processing_hook(self, db_query: AbstractCouchDBQuery, hook: Callable) -> AbstractCouchDBQuery:
        if db_query.post_processors is None:
            db_query.post_processors = []
        db_query.post_processors.append(hook)
        return db_query

    def add_pre_processing_hook(self, db_query: AbstractCouchDBQuery, hook: Callable) -> AbstractCouchDBQuery:
        if db_query.pre_processors is None:
            db_query.pre_processors = []
        db_query.pre_processors.append(hook)
        return db_query
