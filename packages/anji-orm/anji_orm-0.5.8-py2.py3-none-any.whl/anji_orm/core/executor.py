import abc
from importlib import import_module
from typing import Type, TYPE_CHECKING, Dict, Optional, Any, overload, Tuple, TypeVar, Generic
import logging

if TYPE_CHECKING:
    # pylint: disable=unused-import
    from .model import Model
    from .register import AbstractSyncRegisterStrategy, AbstractAsyncRegisterStrategy

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.8"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["AbstractSyncExecutor", "AbstractAsyncExecutor", "fetch"]

_log = logging.getLogger(__name__)

T = TypeVar('T')


class AbstractSyncExecutor(Generic[T]):

    def __init__(self, sync_strategy: 'AbstractSyncRegisterStrategy') -> None:
        self.strategy = sync_strategy

    @abc.abstractmethod
    def send_model(self, model: 'Model') -> Dict:
        pass

    @abc.abstractmethod
    def load_model(self, model: 'Model') -> Tuple[Dict, Optional[Dict]]:
        pass

    @abc.abstractmethod
    def delete_model(self, model: 'Model') -> Dict:
        pass

    @abc.abstractmethod
    def get_model(self, model_cls: Type['Model'], id_) -> Optional['Model']:
        pass

    @abc.abstractmethod
    def execute_query(self, query: T, without_fetch: bool = False):
        pass


class AbstractAsyncExecutor(Generic[T]):

    def __init__(self, async_strategy: 'AbstractAsyncRegisterStrategy') -> None:
        self.strategy = async_strategy

    @abc.abstractmethod
    async def send_model(self, model: 'Model') -> Dict:
        pass

    @abc.abstractmethod
    async def load_model(self, model: 'Model') -> Tuple[Dict, Optional[Dict]]:
        pass

    @abc.abstractmethod
    async def delete_model(self, model: 'Model') -> Dict:
        pass

    @abc.abstractmethod
    async def get_model(self, model_cls: Type['Model'], id_) -> Optional['Model']:
        pass

    @abc.abstractmethod
    async def execute_query(self, query: T, without_fetch: bool = False):
        pass


@overload
def fetch(data_dict: Dict[str, Any], meta: Optional[Dict] = None) -> Optional['Model']:  # pylint: disable=unused-argument
    pass


@overload
def fetch(data_dict: Dict[str, Any], meta: Optional[Dict] = None) -> Dict[str, Any]:  # pylint: disable=function-redefined, unused-argument
    pass


def fetch(data_dict: Dict[str, Any], meta: Optional[Dict] = None):  # pylint: disable=function-redefined
    if '_python_info' not in data_dict:
        # Return just this dict, if he cannot be recognized as orm model
        return data_dict
    class_module = import_module(data_dict['_python_info']['module_name'])
    class_object = getattr(class_module, data_dict['_python_info']['class_name'], None)
    if class_object is None:
        _log.warning('Model record %s cannot be parsed, because class wasnt found!', data_dict['id'])
        return None
    obj = class_object(id=data_dict['id'])
    obj.load(data_dict, meta=meta)
    return obj
