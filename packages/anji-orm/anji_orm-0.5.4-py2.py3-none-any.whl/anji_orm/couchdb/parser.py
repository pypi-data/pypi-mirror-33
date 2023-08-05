# pylint: disable=no-self-use
from datetime import datetime
from typing import Dict, Type, Callable
import operator
from functools import partial

from toolz.functoolz import compose

from ..core import (
    QueryBiStatement, StatementType, Interval, BaseQueryParser,
    QueryBuildException, SamplingType, Model, abstraction_ignore_log,
    QueryRowOrderMark, AggregationType, QueryRow, QueryAst,
    QueryChangeStatement
)

from .view_ast import CouchDBMap, CouchDBReduce
from .utils import serialize_datetime, DDOC_FOR_GENERATED_VIEWS_NAME, couchdb_dict_deserialize

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.4"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['CouchDBQueryParser']


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


def _convert_to_compatiable_event_format(model_cls: Type[Model], event: Dict) -> Dict:
    result = {}
    if not event:
        return event
    event_data = event['data']
    result['type'] = 'change' if event_data.get('deleted') is None else 'remove'
    couchdb_dict_deserialize(model_cls, event_data['doc'])
    result['doc'] = event_data['doc']
    return result


async def _async_map(function, async_generator):
    async for element in async_generator:
        yield function(element)

_itemgetter_rows = operator.itemgetter("rows")  # pylint: disable=invalid-name
_itemgetter_doc = operator.itemgetter("doc")  # pylint: disable=invalid-name
_aggregation_result_getter = compose(operator.itemgetter('value'), next)  # pylint: disable=invalid-name
_aggregation_group_result_converter = compose(dict, partial(map, lambda x: (x['key'], x['value'])))  # pylint: disable=invalid-name


class CouchDBQueryParser(BaseQueryParser[Dict]):

    __index_selection__ = False
    __sample_emulation__ = True
    __processing_hook_support__ = True
    __target_database__ = 'CouchDB'

    def build_empty_query(self, _db_query: Dict) -> Dict:
        return {
            "selector": {}
        }

    def initial_query(self, _model_class: Type[Model], query: QueryAst) -> Dict:
        return {
            "selector": {},
            '_context': {
                'table_name': _model_class._table,
                'query_identity': str(query),
                'url_method': "_find"
            }
        }

    def build_table_query(self, db_query: Dict, _model_class: Type[Model]) -> Dict:
        db_query["selector"] = {"_id": {"$gt": None}}
        return db_query

    def process_simple_statement(self, db_query: Dict, simple_statement: QueryBiStatement) -> Dict:
        row_name = simple_statement.left.row_name
        row_query_dict = db_query['selector'].setdefault(row_name, {})
        if simple_statement.statement_type == StatementType.isin:
            row_query_dict['$in'] = _ensure_query_arg_compitability(simple_statement.right)
        elif simple_statement.statement_type == StatementType.bound:
            interval: Interval = simple_statement.right
            right_bound_key = "$lte" if interval.right_close else "$lt"
            left_bound_key = "$gte" if interval.left_close else "$gt"
            row_query_dict[left_bound_key] = _ensure_query_arg_compitability(interval.left_bound)
            row_query_dict[right_bound_key] = _ensure_query_arg_compitability(interval.right_bound)
        else:
            db_query["selector"][row_name] = {
                STATEMENT_MAPPING[simple_statement.statement_type]: _ensure_query_arg_compitability(simple_statement.right)
            }
        return db_query

    def process_complicated_statement(self, search_query: Dict, statement: QueryBiStatement) -> Dict:
        if 'ddoc_view' in search_query['_context']:
            search_query['_context']['ddoc_view']['value']['map'].filter.add(statement)
        else:
            base_map = CouchDBMap(search_query)
            base_map.filter.add(statement)
            search_query['_context']["ddoc_view"] = {
                "name": str(search_query["_context"]['query_identity']),
                "value": {
                    "map": base_map,
                }
            }
        return search_query

    def process_sampling_statement(self, db_query: Dict, sampling_type: SamplingType, sampling_arg) -> Dict:
        if sampling_type == SamplingType.order_by:
            db_query['sort'] = []
            general_direction = None
            order_mark: QueryRowOrderMark
            for order_mark in sampling_arg:
                if general_direction is None:
                    general_direction = order_mark.order
                if general_direction == order_mark.order:
                    db_query['sort'].append(order_mark.row_name)
                else:
                    abstraction_ignore_log.warning(
                        "CouchDB cannot sort in multi direction, so"
                        " sorting by %s in %s order was ignored",
                        order_mark.row_name, order_mark.order
                    )
            if general_direction != 'asc':
                db_query['sort'] = [{x: 'desc'} for x in db_query['sort']]
        else:
            if sampling_type.name in db_query:
                raise QueryBuildException(f"Cannot use {sampling_type.name} sampling two times!")
            db_query[sampling_type.name] = sampling_arg
        return db_query

    def add_post_processing_hook(self, db_query: Dict, hook: Callable) -> Dict:
        db_query['_context'].setdefault('post_processors', []).append(hook)
        return db_query

    def add_pre_processing_hook(self, db_query: Dict, hook: Callable) -> Dict:
        db_query['_context'].setdefault('pre_processors', []).append(hook)
        return db_query

    def process_aggregation_statement(
            self, db_query: Dict, aggregation_type: AggregationType,
            row: QueryRow) -> Dict:
        if 'ddoc_view' in db_query['_context']:
            db_query['_context']['ddoc_view']['value']['map'].filter.add_parsed(db_query['selector'])
            db_query['_context']['ddoc_view']['value']['map'].emit_row = row
            db_query['_context']['ddoc_view']['value']['reduce'] = CouchDBReduce(aggregation_type)
        else:
            db_query['_context']["ddoc_view"] = {
                "name": str(db_query["_context"]['query_identity']),
                "value": {
                    "map": CouchDBMap(db_query, row),
                    "reduce": CouchDBReduce(aggregation_type)
                }
            }
        if db_query.get('params', {}).get('group', None):
            # Avoiding get first result of aggregation in case of grouping
            self.add_post_processing_hook(db_query, _aggregation_group_result_converter)
        else:
            self.add_post_processing_hook(db_query, _aggregation_result_getter)
        return db_query

    def process_group_statement(self, db_query: Dict, group_row: QueryRow) -> Dict:
        if 'ddoc_view' in db_query['_context']:
            db_query['_context']['ddoc_view']['value']['map'].emit_key_field = group_row
        else:
            base_map = CouchDBMap(db_query)
            base_map.emit_key_field = group_row
            db_query['_context']["ddoc_view"] = {
                "name": str(db_query["_context"]['query_identity']),
                "value": {
                    "map": base_map,
                }
            }
        db_query.setdefault('params', {})['group'] = 'true'
        return db_query

    def process_change_statement(self, db_query: Dict, change_statement: QueryChangeStatement) -> Dict:
        if 'ddoc_view' in db_query['_context']:
            pass
        else:
            db_query['_context']['url_method'] = "_changes"
            db_query.setdefault('params', {}).update({
                "include_docs": "true",
                "feed": "eventsource",
                "filter": "_selector",
                "since": '0' if change_statement.with_initial else 'now'
            })
        event_processing = partial(
            _async_map,
            partial(_convert_to_compatiable_event_format, change_statement.model_ref)
        )
        self.add_post_processing_hook(db_query, event_processing)
        return db_query

    def query_post_processing(self, db_query: Dict, model_class: Type[Model]) -> Dict:
        if 'ddoc_view' in db_query['_context']:
            return {
                "url": (
                    f"{model_class._table}/_design/"
                    f"{DDOC_FOR_GENERATED_VIEWS_NAME}/_view/{db_query['_context']['ddoc_view']['name']}"
                ),
                "params": db_query.pop('params', None),
                "method": "get",
                '_context': db_query.pop("_context", None)
            }
        return {
            "url": f"{model_class._table}/{db_query['_context'].pop('url_method')}",
            "method": "post",
            "params": db_query.pop('params', None),
            "json": db_query,
            '_context': db_query.pop("_context", None)
        }
