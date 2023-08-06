from typing import Dict, Any, List, Optional, Tuple
from abc import ABCMeta
import logging
from weakref import WeakValueDictionary

from .fields import DatetimeField, AbstractField, JsonField, StringField
from .ast import QueryAst, QueryTable
from .indexes import IndexPolicy, IndexPolicySetting, IndexPolicySettings
from .register import orm_register
from .utils import merge_dicts

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.8"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = ['SharedEnv', 'Model', 'ModelMetaclass', 'ModifyDisallowException']

MODEL_FIELDS_CONTROL = {
    '_aggregate_dict': ['_fields', '_field_marks'],
    '_aggregate_sets': ['_primary_keys'],
    '_inherit_field': ['_table'],
    # '_deep_merge_dict': ['_index_policy_settings']
}

BASE_COLLECTION_TYPE = (list, tuple)

_log = logging.getLogger(__name__)


class ModifyDisallowException(Exception):
    """
    Exception that raises when you try change `Model` class field that blocked for changes
    """
    pass


class ModelMetaclass(ABCMeta):

    @classmethod
    def _aggregate_sets(mcs, bases, namespace, field):
        actual_field = set()
        for base_class in bases:
            if hasattr(base_class, field):
                actual_field.update(getattr(base_class, field))
        if namespace.get(field, None):
            actual_field.update(namespace.get(field))
        namespace[field] = actual_field

    @classmethod
    def _aggregate_dict(mcs, bases, namespace, field):
        actual_field = {}
        for base_class in bases:
            if hasattr(base_class, field):
                actual_field.update(getattr(base_class, field))
        if namespace.get(field, None):
            actual_field.update(namespace.get(field))
        namespace[field] = actual_field

    @classmethod
    def _inherit_field(mcs, bases, namespace: Dict, field: str):
        current_field_exists = field in namespace
        if not current_field_exists:
            for base_class in bases:
                if hasattr(base_class, field):
                    namespace[field] = getattr(base_class, field)
                    break

    @classmethod
    def _deep_merge_dict(mcs, bases, namespace: Dict, field: str):
        actual_field: Dict = {}
        for base_class in bases:
            if hasattr(base_class, field):
                merge_dicts(getattr(base_class, field), actual_field)
        if namespace.get(field, None):
            merge_dicts(namespace.get(field), actual_field)
        namespace[field] = actual_field

    @classmethod
    def _block_modify(mcs, bases, namespace, field):
        if namespace.get(field) and (len(bases) > 1 or (len(bases) == 1 and bases[0] != object)):
            raise ModifyDisallowException('Field {} cannot be modified in child classes'.format(field))

    @classmethod
    def _fetch_fields(mcs, namespace):
        fields = namespace.get('_fields', None) or {}
        field_marks = {}
        primary_keys = set()
        remove_list = []
        for attr_name, attr in namespace.items():
            if getattr(attr, '_anji_orm_field', None):
                remove_list.append(attr_name)
                fields[attr_name] = attr
                attr.name = attr_name
                if attr.field_marks:
                    for field_mark in attr.field_marks:
                        field_marks[field_mark] = attr_name
                if attr.definer:
                    primary_keys.add(attr_name)
        primary_keys = sorted(primary_keys)
        namespace['_fields'] = fields
        namespace['_field_marks'] = field_marks
        namespace['_primary_keys'] = primary_keys

    @classmethod
    def _check_primary_keys(mcs, namespace):
        for field_name, field_item in namespace['_fields'].items():
            if not field_item.definer and field_name in namespace['_primary_keys']:
                namespace['_primary_keys'].remove(field_name)

    def __new__(mcs, name, bases, namespace, **kwargs):

        # Process fields

        mcs._fetch_fields(namespace)

        # Execute control actions

        for key, value in MODEL_FIELDS_CONTROL.items():
            if hasattr(mcs, key):
                for field in value:
                    getattr(mcs, key)(bases, namespace, field)

        mcs._check_primary_keys(namespace)

        if '__slots__' not in namespace:
            namespace['__slots__'] = ()

        # Process with register
        result = super().__new__(mcs, name, bases, namespace, **kwargs)

        if namespace.get('_table'):
            orm_register.add_table(namespace.get('_table'), result)

        return result


class RelactionCache:  # pylint: disable=too-few-public-methods

    def __init__(self):
        self._models_cache = {}

    def __getitem__(self, key: str) -> WeakValueDictionary:
        return self._models_cache.setdefault(key, WeakValueDictionary())


class SharedEnv:

    def __init__(self):
        self._env = {}
        self.share('relation_cache', RelactionCache())

    def share(self, key: str, value: Any) -> None:
        self._env[key] = value

    def __getattr__(self, key: str) -> Any:
        if key in self._env:
            return self._env[key]
        raise AttributeError


class Model(object, metaclass=ModelMetaclass):  # pylint: disable=too-many-public-methods
    """
    Base class with core logic for rethinkdb usage.
    For usage you must define _table and _fields section.
    All object fields, that defined in _fields will be processed in send() and load() methods
    """

    _table = ''
    _fields: Dict[str, AbstractField] = {}
    _field_marks: Dict[str, AbstractField] = {}
    _primary_keys: List[str] = []
    _index_policy: IndexPolicy = IndexPolicy.single

    _index_policy_settings: IndexPolicySettings = {
        IndexPolicySetting.only_single_index: ('_schema_version',)
    }

    shared: SharedEnv = SharedEnv()

    orm_last_write_timestamp = DatetimeField(service=True, displayed=False)
    _python_info = JsonField(service=True, displayed=False, compute_function='_build_python_info', stored=True)
    _schema_version = StringField(service=True, displayed=False, default='v0.4', secondary_index=True)
    id = StringField()

    __slots__ = ('_meta', '_values')

    def __init__(self, **kwargs) -> None:
        """
        Complex init method for rethinkdb method.
        Next tasks will be executed:
        1. Create all fields, that defined in _fields, for object
        3. Set base fields, like connection link.
            Additionally can set id field in some cases (for example in fetch method)
        4. Create table field, to be used in queries
        """
        self._values: Dict[str, Any] = dict()
        self._meta: Dict = dict()
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _build_python_info(self) -> Dict[str, str]:
        return {
            'module_name': self.__class__.__module__,
            'class_name': self.__class__.__name__
        }

    def to_dict(self, full_dict: bool = False) -> Dict[str, Any]:
        """
        Utility method to generate dict from object.
        Used to send information to rethinkdb.

        :param full_dict: Build full data dict with non-stored fields
        """
        base_dict = {}
        for field_name, field_item in self._fields.items():
            if not full_dict and field_item.compute_function is not None and not field_item.stored:
                _log.debug('Skip field %s as not stored field', field_name)
                continue
            base_dict[field_name] = field_item.real_value(self)
        # Ignore id when empty
        if not base_dict['id']:
            del base_dict['id']
        return base_dict

    def _apply_update_dict(self, update_dict: Dict[str, Any]) -> None:
        for _, field in self._fields.items():
            required_keys = field.update_keys()
            for key in required_keys:
                value = update_dict.get(key, None)
                if value is not None:
                    field.update_value(self, key, value)

    def from_dict(self, data_dict: Dict[str, Any], meta: Dict = None) -> None:
        """
        Load model record from dict

        :param data_dict: dict with data from RethinkDB
        """
        for field_name, field_item in self._fields.items():
            if field_name in data_dict and (field_item.compute_function is None or field_item.cacheable):
                setattr(self, field_name, data_dict[field_name])
        if meta:
            self._meta = meta

    def to_describe_dict(self, definer_skip: bool = False) -> Dict[str, str]:
        """
        Convert record to dict with pair "Pretty field name" "Pretty field value".
        By default only field with `displayed` option will be in dict.

        :param definer_skip: Additional to not displayed skip definer fields
        """
        fields = {}
        for field_name, field_item in self._fields.items():
            if field_item.displayed and not (definer_skip and field_item.definer) and getattr(self, field_name) is not None:
                fields[field_item.description] = field_item.format(getattr(self, field_name))
        return fields

    async def async_to_describe_dict(self, definer_skip: bool = False) -> Dict[str, str]:
        fields = {}
        for field_name, field_item in self._fields.items():
            if field_item.displayed and not (definer_skip and field_item.definer) and getattr(self, field_name) is not None:
                fields[field_item.description] = await field_item.async_format(getattr(self, field_name))
        return fields

    @classmethod
    def build_index_list(cls) -> List[Tuple[str, List[str]]]:
        return cls._index_policy.value.build_index_list(cls)  # pylint: disable=no-member

    def load(self, data_dict=None, meta=None) -> None:
        if not data_dict:
            data_dict, meta = self.shared.executor.load_model(self)
        self.from_dict(data_dict, meta=meta)

    async def async_load(self, data_dict=None, meta=None) -> None:
        if not data_dict:
            data_dict, meta = await self.shared.executor.load_model(self)
        self.from_dict(data_dict, meta=meta)

    def send(self) -> None:
        self.shared.executor.send_model(self)

    async def async_send(self) -> None:
        await self.shared.executor.send_model(self)

    def delete(self) -> None:
        self.shared.executor.delete_model(self)

    async def async_delete(self) -> None:
        await self.shared.executor.delete_model(self)

    @classmethod
    def get(cls, id_) -> Optional['Model']:
        return cls.shared.executor.get_model(cls, id_)

    @classmethod
    async def async_get(cls, id_) -> Optional['Model']:
        return await cls.shared.executor.get_model(cls, id_)

    @classmethod
    def all(cls) -> QueryAst:
        return QueryTable(cls._table, model_ref=cls)

    def update(self, update_dict: Dict[str, Any]) -> None:
        self._apply_update_dict(update_dict)
        self.send()

    async def async_update(self, update_dict: Dict[str, Any]) -> None:
        self._apply_update_dict(update_dict)
        await self.async_send()

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        for field_name, field in self._fields.items():
            if field.service:
                continue
            if getattr(self, field_name) != getattr(other, field_name):
                return False
        return True

    def __repr__(self) -> str:
        values = ", ".join(
            f"{key}={getattr(self, key)}" for key, field in self._fields.items()
            if field.displayed
        )
        return f'{self.__class__.__name__}[{values}]'
