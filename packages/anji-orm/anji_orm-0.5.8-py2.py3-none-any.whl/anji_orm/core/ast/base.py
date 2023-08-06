import logging
from typing import Any, Optional, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ..model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.8"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'QueryAst', "QueryBuildException"
]

_log = logging.getLogger(__name__)


class QueryBuildException(Exception):

    pass


class QueryAst:

    __slots__ = ('model_ref', )

    def __init__(self, model_ref: Optional[Type['Model']] = None) -> None:
        self.model_ref: Optional[Type['Model']] = model_ref

    def _adapt_query(self) -> None:
        pass

    def build_query(self) -> Any:

        if self.model_ref is None:
            raise QueryBuildException("Cannot build query without model link!")
        self._adapt_query()
        return self.model_ref.shared.query_parser.parse_query(self)

    def run(self, without_fetch: bool = False):
        if self.model_ref is None:
            raise QueryBuildException("Cannot build query without model link!")
        return self.model_ref.shared.executor.execute_query(self.build_query(), without_fetch=without_fetch)

    async def async_run(self, without_fetch: bool = False):
        if self.model_ref is None:
            raise QueryBuildException("Cannot build query without model link!")
        return await self.model_ref.shared.executor.execute_query(self.build_query(), without_fetch=without_fetch)
