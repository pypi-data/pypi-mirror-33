import abc
import asyncio
from typing import Dict, Any, List, Type, TYPE_CHECKING, Tuple
from datetime import datetime
from urllib.parse import urlparse

from aenum import Enum, enum

from .executor import AbstractSyncExecutor, AbstractAsyncExecutor
from .parser import AbstractQueryParser
from .utils import import_class

if TYPE_CHECKING:
    from .model import Model  # pylint: disable=unused-import

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.7"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = [
    'orm_register', 'AbstractAsyncRegisterStrategy',
    'AbstractSyncRegisterStrategy', 'AbstractBackendAdapter'
]


class RegisterModeMissmatch(Exception):
    """
    Base exception, that caused when you try to use sync commands in async mode
    and async commands in sync mode
    """


class RegistryProtocol(Enum):

    rethinkdb = enum(
        sync_strategy='anji_orm.rethinkdb.SyncRethinkDBRegisterStrategy',
        async_strategy='anji_orm.rethinkdb.AsyncRethinkDBRegisterStrategy'
    )

    couchdb = enum(
        sync_strategy='anji_orm.couchdb.SyncCouchDBRegisterStrategy',
        async_strategy='anji_orm.couchdb.AsyncCouchDBRegisterStrategy'
    )


class AbstractBackendAdapter(abc.ABC):

    @abc.abstractmethod
    def utcnow(self) -> datetime:
        pass

    @abc.abstractmethod
    def now(self) -> datetime:
        pass

    @abc.abstractmethod
    def ensure_datetime_compatibility(self, value: datetime) -> datetime:
        pass

    @abc.abstractmethod
    def ensure_compatibility(self, value):
        pass


class AbstractAsyncRegisterStrategy(abc.ABC):

    @abc.abstractmethod
    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:
        pass

    @property
    @abc.abstractmethod
    def executor(self) -> AbstractAsyncExecutor:
        pass

    @property
    @abc.abstractmethod
    def query_parser(self) -> AbstractQueryParser:
        pass

    @property
    @abc.abstractmethod
    def backend_adapter(self) -> AbstractBackendAdapter:
        pass

    @abc.abstractmethod
    async def execute_query(self, query: Any) -> Any:
        pass

    @abc.abstractmethod
    async def load(self) -> None:
        pass

    @abc.abstractmethod
    async def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        pass

    @abc.abstractmethod
    async def drop_index(self, table_name: str, index_name: str) -> None:
        pass

    @abc.abstractmethod
    async def list_indexes(self, table_name: str) -> List[str]:
        pass

    @abc.abstractmethod
    async def create_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    async def drop_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    async def list_tables(self) -> List[str]:
        pass

    async def ensure_tables(self, table_list: List[str]) -> None:
        exists_tables = await self.list_tables()
        coroutines_for_tables = [
            self.create_table(table)
            for table in table_list
            if table not in exists_tables
        ]
        if coroutines_for_tables:
            await asyncio.wait(coroutines_for_tables)

    async def ensure_indexes(self, table_name: str, table_models: List[Type['Model']]) -> None:
        current_index_list = await self.list_indexes(table_name)
        orm_required_indexes: List[Tuple[str, List[str]]] = []
        for table_model in table_models:
            indexes = table_model.build_index_list()
            if indexes:
                orm_required_indexes.extend(indexes)
        # Create new indexes
        # TODO: thinks about many awaiting coroutines, at least same as pool size
        for index_name, index_fields in orm_required_indexes:
            if index_name not in current_index_list:
                await self.create_index(table_name, index_name, index_fields)
                current_index_list.append(index_name)
        orm_required_indexes_name: List[str] = [x[0] for x in orm_required_indexes]
        for index in (
                index for index in current_index_list if index
                not in orm_required_indexes_name):
            await self.drop_index(table_name, index)

    @abc.abstractmethod
    async def close(self) -> None:
        pass


class AbstractSyncRegisterStrategy(abc.ABC):

    @abc.abstractmethod
    def __init__(self, connection_uri: str, **pool_kwargs: Any) -> None:
        pass

    @property
    @abc.abstractmethod
    def executor(self) -> AbstractSyncExecutor:
        pass

    @property
    @abc.abstractmethod
    def query_parser(self) -> AbstractQueryParser:
        pass

    @property
    @abc.abstractmethod
    def backend_adapter(self) -> AbstractBackendAdapter:
        pass

    @abc.abstractmethod
    def execute_query(self, query: Any) -> Any:
        pass

    @abc.abstractmethod
    def load(self) -> None:
        pass

    @abc.abstractmethod
    def create_index(
            self, table_name: str,
            index_name: str, index_fields: List[str]) -> None:
        pass

    @abc.abstractmethod
    def drop_index(self, table_name: str, index_name: str) -> None:
        pass

    @abc.abstractmethod
    def list_indexes(self, table_name: str) -> List[str]:
        pass

    @abc.abstractmethod
    def create_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    def drop_table(self, table_name: str) -> None:
        pass

    @abc.abstractmethod
    def list_tables(self) -> List[str]:
        pass

    def ensure_tables(self, table_list: List[str]) -> None:
        exists_tables = self.list_tables()
        for table in table_list:
            if table not in exists_tables:
                self.create_table(table)

    def ensure_indexes(self, table_name: str, table_models: List[Type['Model']]) -> None:
        current_index_list = self.list_indexes(table_name)
        orm_required_indexes: List[Tuple[str, List[str]]] = []
        for table_model in table_models:
            indexes = table_model.build_index_list()
            if indexes:
                orm_required_indexes.extend(indexes)
        # Create new indexes
        for index_name, index_fields in orm_required_indexes:
            if index_name not in current_index_list:
                self.create_index(table_name, index_name, index_fields)
                current_index_list.append(index_name)
        orm_required_indexes_name: List[str] = [x[0] for x in orm_required_indexes]
        for index in (
                index for index in current_index_list if index
                not in orm_required_indexes_name):
            self.drop_index(table_name, index)

    @abc.abstractmethod
    def close(self) -> None:
        pass


class ORMRegister(object):

    """
    Register object that store any information about models, tables.
    Store and control pool and wrap logic.
    """

    def __init__(self) -> None:
        super().__init__()
        self.async_loop: asyncio.AbstractEventLoop
        self._backend_adapter: AbstractBackendAdapter
        self.tables: List[str] = []
        self.tables_model_link: Dict[str, List[Type['Model']]] = {}
        self.sync_strategy: AbstractSyncRegisterStrategy
        self.async_strategy: AbstractAsyncRegisterStrategy
        self.async_mode: bool = False

    def init(self, connection_uri: str, pool_kwargs: Dict, async_mode: bool = False) -> None:
        from .model import Model  # pylint: disable=redefined-outer-name

        self.async_mode = async_mode

        required_protocol = urlparse(connection_uri).scheme

        protocol_enum = RegistryProtocol.__members__.get(required_protocol, None)
        if protocol_enum is None:
            raise ValueError(f"Cannot find implementation for {connection_uri}")

        if async_mode:
            self.async_strategy = import_class(
                protocol_enum.value.kwds['async_strategy']
            )(connection_uri, **pool_kwargs)
        else:
            self.sync_strategy = import_class(
                protocol_enum.value.kwds['sync_strategy']
            )(connection_uri, **pool_kwargs)
        if async_mode:
            Model.shared.share('executor', self.async_strategy.executor)
            Model.shared.share('query_parser', self.async_strategy.query_parser)
            Model.shared.share('backend_adapter', self.async_strategy.backend_adapter)
        else:
            Model.shared.share('executor', self.sync_strategy.executor)
            Model.shared.share('query_parser', self.sync_strategy.query_parser)
            Model.shared.share('backend_adapter', self.sync_strategy.backend_adapter)
        self._backend_adapter = Model.shared.backend_adapter

    def add_table(self, table: str, model_cls: Type['Model']):
        if table and (table not in self.tables):
            self.tables.append(table)
        self.tables_model_link.setdefault(table, []).append(model_cls)

    async def async_load(self, database_setup=True) -> None:
        await self.async_strategy.load()
        self.async_loop = asyncio.get_event_loop()
        if database_setup:
            await self.async_strategy.ensure_tables(self.tables)
            for table_name, table_models in self.tables_model_link.items():
                await self.async_strategy.ensure_indexes(table_name, table_models)

    def load(self, database_setup=True) -> None:
        self.sync_strategy.load()
        if database_setup:
            self.sync_strategy.ensure_tables(self.tables)
            for table_name, table_models in self.tables_model_link.items():
                self.sync_strategy.ensure_indexes(table_name, table_models)

    def close(self) -> None:
        self.sync_strategy.close()

    async def async_close(self) -> None:
        await self.async_strategy.close()

    def current_datetime(self) -> datetime:
        return self._backend_adapter.now()

    def current_utc_datetime(self) -> datetime:
        return self._backend_adapter.utcnow()

    def ensure_datetime_compatibility(self, value: datetime) -> datetime:
        return self._backend_adapter.ensure_datetime_compatibility(value)

    def ensure_compatibility(self, value: Any) -> Any:
        return self._backend_adapter.ensure_compatibility(value)


orm_register = ORMRegister()  # pylint: disable=invalid-name
