from typing import Type

from ...core import BaseQueryParser, QueryAst, Model
from ..lib import AbstractCouchDBQuery, DummyCouchDBQuery
from .filter_parser import CouchDBFilterQueryParser
from .transformation_parser import CouchDBTransformationQueryParser
from .operation_parser import CouchDBOperationQueryParser

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.7"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['CouchDBQueryParser']


class CouchDBQueryParser(BaseQueryParser[AbstractCouchDBQuery]):  # pylint: disable=too-few-public-methods

    __filter_parser__ = CouchDBFilterQueryParser
    __transformation_parser__ = CouchDBTransformationQueryParser
    __operation_parser__ = CouchDBOperationQueryParser

    def initial_query(self, model_class: Type[Model], query: QueryAst) -> AbstractCouchDBQuery:  # pylint: disable=no-self-use
        base_query = DummyCouchDBQuery(str(query))
        base_query.table_name = model_class._table
        return base_query
