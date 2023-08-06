import asyncio
from typing import Tuple, Type, Any, List, Iterable, Union, overload
from enum import Enum
from datetime import datetime
import inspect
import logging
import functools

import humanize

from ..ast.rows import QueryRow, BooleanQueryRow, DictQueryRow
from ..utils import NotYetImplementException, prettify_value
from ..register import orm_register

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.8"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'AbstractField', 'StringField', 'IntField', 'BooleanField', 'SelectionField',
    'EnumField', 'FloatField', 'DatetimeField', 'ListField', 'DictField', 'JsonField',
]

_log = logging.getLogger(__name__)

LIST_FIELD_SEPARATOR = '|'


class AbstractField(object):  # pylint:disable=too-many-instance-attributes

    """
    Abstract ORM field class. Used to describe base logic and provide unified type check
    """

    _anji_orm_field: bool = True

    __slots__ = (
        'param_type', 'default', 'description', 'optional',
        'reconfigurable', 'definer', 'service', 'field_marks',
        'secondary_index', 'displayed', 'compute_function', 'cacheable',
        'stored', 'name'
    )

    @overload
    def __init__(self, param_type: Type, default: Any = None, **kwargs) -> None:
        pass

    @overload
    def __init__(self, param_type: Tuple[Type, ...], default: Any = None, **kwargs) -> None:  # pylint: disable=function-redefined
        pass

    def __init__(self, param_type, default=None, **kwargs):  # pylint: disable=function-redefined
        """
        Init function for ORM fields. Provide parameter checks with assertion

        :param param_type: Type class, that will be used for type checking
        :param default: Field default value, should be strict value or callable function.  Default value is None.
        :param description: Field description, mostly used for automatic generated commands. Default value is empty string.
        :type description: str
        :param optional: If true, this field is optional.  Default value is False.
        :type optional: bool
        :param reconfigurable: If true, this field can be changed via configure commands.  Default value is False.
        :type reconfigurable: bool
        :param definer: If true, this field should be unique per record.  Default value is False.
        :type definer: bool
        :param service: If true, this field used only in internal bot logic.  Default value is False.
        :type service: bool
        :param field_marks: Additional field marks, to use in internal logic.  Default value is None.
        :type field_marks: List[str]
        :param secondary_index: If true, ORM will build secondary_index on this field.  Default value is False.
        :type secondary_index: bool
        :param displayed: If true, this field will be displayed on chat report.  Default value is True.
        :type displayed: bool
        :param compute_function: Make field computable and use this function to calculate field value.  Default value is False
        :type compute_function: Callable
        :param cacheable: If false, field value will be recomputed every time on access. Default value is True.
        :type cacheable: bool
        :param stored: Make field stored in database, if field computed, default False
        :type stored: bool
        """
        # Setup fields
        self.param_type: Type = param_type
        self.default: Any = default
        self.description: str = kwargs.pop('description', '')
        self.optional: bool = kwargs.pop('optional', False)
        self.reconfigurable: bool = kwargs.pop('reconfigurable', False)
        self.definer: bool = kwargs.pop('definer', False)
        self.service: bool = kwargs.pop('service', False)
        self.field_marks: List[str] = kwargs.pop('field_marks', None)
        self.secondary_index: bool = kwargs.pop('secondary_index', False)
        self.displayed: bool = kwargs.pop('displayed', True)
        self.compute_function: str = kwargs.pop('compute_function', None)
        self.cacheable: bool = kwargs.pop('cacheable', True)
        self.stored: bool = kwargs.pop('stored', False)
        # Check rules
        assert not kwargs, f"Cannot parse {kwargs} configuration. What is it?"
        assert not (self.optional and self.definer), f"Field {self.description} should be optional xor definer"
        assert not (self.reconfigurable and self.definer), f"Field {self.description} should be reconfigurable xor definer"
        assert not (self.service and self.definer), f"Field {self.description} should be service xor definer"
        assert self.cacheable or (not self.cacheable and self.compute_function), "Only compute field can be not cacheable"
        compute_function_check = not self.compute_function or (callable(self.compute_function) or isinstance(self.compute_function, str))
        assert compute_function_check, "Compute function should be or callabe, or name of model function"
        # Name will be set by Model Metaclass
        # when field list be fetched
        self.name: str = None

    @functools.lru_cache(None)
    def _query_row(self, model_instance) -> QueryRow:
        return QueryRow(self.name, secondary_index=self.secondary_index, model_ref=model_instance)

    def __set_name__(self, owner, name) -> None:
        self.name = name

    def _get_default(self):
        if callable(self.default):
            return self.default()
        return self.default

    def update_keys(self) -> Tuple:
        return (self.name,)

    def update_value(self, instance, _key: str, value) -> None:
        setattr(instance, self.name, value)

    def format(self, value) -> str:  # pylint: disable=no-self-use
        """
        Prettify formation function, that used to disable this variable in :py:func:`~anji_orm.model.Model.to_describe_dict` function.
        Also can be used for formatting itself
        """
        return str(value)

    async def async_format(self, value) -> str:  # pylint: disable=no-self-use
        return self.format(value)

    def real_value(self, model_record):
        """
        Based on __get__ method, but can be used to split overrided __get__ method
        like for LinkField from real infomration
        """
        return prettify_value(self.__get__(model_record, None))

    def _compute_value(self, instance):
        result = None
        if callable(self.compute_function):
            result = self.compute_function(instance)
        else:
            result = getattr(instance, self.compute_function)()
        if inspect.iscoroutine(result):
            result = asyncio.ensure_future(result)
        return result

    def _compute_get_logic(self, instance):
        if not self.cacheable:
            return self._compute_value(instance)
        result = instance._values.get(self.name)
        if result is None:
            result = self._compute_value(instance)
            instance._values[self.name] = result
        return result

    def __get__(self, instance, instance_type):
        if instance is None:
            return self._query_row(instance_type)
        if self.compute_function:
            return self._compute_get_logic(instance)
        try:
            return instance._values[self.name]
        except KeyError:
            result = self._get_default()
            self.__set__(instance, result)
            return result

    def __set__(self, instance, value) -> None:
        if value is not None and not isinstance(value, self.param_type):
            raise ValueError(f'Field {self.name} value should have {str(self.param_type)} type instead of {value}')
        if self.compute_function is not None:
            if not self.stored:
                raise ValueError("You cannot set value to compute field")
            if not self.cacheable:
                return
        instance._values[self.name] = value


class StringField(AbstractField):

    __slots__ = ()

    def __init__(self, default='', **kwargs) -> None:
        super().__init__(
            str,
            default=default,
            **kwargs
        )


class IntField(AbstractField):

    __slots__ = ()

    def __init__(self, default=0, **kwargs) -> None:
        super().__init__(
            int,
            default=default,
            **kwargs
        )


class BooleanField(AbstractField):

    __slots__ = ()

    def __init__(self, default=False, **kwargs) -> None:
        super().__init__(
            bool,
            default=default,
            **kwargs
        )

    @functools.lru_cache(None)
    def _query_row(self, model_instance) -> QueryRow:
        return BooleanQueryRow(self.name, self.secondary_index, model_ref=model_instance)


class SelectionField(AbstractField):

    __slots__ = ('variants', )

    def __init__(self, variants: List[List], default=None, **kwargs) -> None:
        assert variants, "You must define some variants"
        if default is None:
            default = variants[0]
        super().__init__(
            str,
            default=default,
            **kwargs
        )
        self.variants = variants

    def __set__(self, instance, value) -> None:
        if value is not None and value not in self.variants:
            raise ValueError(f'Field {self.name} value should be in range {str(self.variants)} type instead of {value}')
        instance._values[self.name] = value


class EnumField(AbstractField):

    __slots__ = ('variants', )

    def __init__(self, enum_class: Type[Union[Enum, Iterable]], default=None, **kwargs) -> None:
        self.variants: List[Enum] = list(enum_class)  # type: ignore
        assert self.variants, f"You must define some child in Enum class {enum_class}"
        if default is None:
            default = self.variants[0]
        super().__init__(
            enum_class,
            default=default,
            **kwargs
        )

    def __set__(self, instance, value):
        if value is not None:
            if value in self.param_type.__members__:
                value = self.param_type[value]
            if value not in self.variants:
                raise ValueError(f'Field {self.name} value should be in range {str(self.variants)} type instead of {value}')
        instance._values[self.name] = value


class FloatField(AbstractField):

    __slots__ = ('decimal_format', )

    def __init__(self, default=0.0, decimal_format: str = "{0:.2f}", **kwargs) -> None:
        super().__init__(
            float,
            default=default,
            **kwargs
        )
        self.decimal_format = decimal_format

    def format(self, value) -> str:
        return self.decimal_format.format(value)

    def __set__(self, instance, value):
        """
        Override to fix zero value in rethinkdb
        """
        if isinstance(value, int):
            value = float(value)
        super().__set__(instance, value)


class DatetimeField(AbstractField):

    __slots__ = ()

    def __init__(self, default=orm_register.current_datetime, **kwargs) -> None:
        super().__init__(
            datetime,
            default=default,
            **kwargs
        )

    def format(self, value: datetime) -> str:
        return f"{humanize.naturaldate(value)} at {value.strftime('%H:%M:%S')}"

    def __set__(self, instance, value):
        """
        Override to correct datetime for backend
        """
        super().__set__(instance, orm_register.ensure_datetime_compatibility(value))


class ListField(AbstractField):

    __slots__ = ()

    def __init__(self, default=None, **kwargs) -> None:
        if default is None:
            default = list
        assert not kwargs.get('secondary_index', None), "Currently this is not supported by orm and query builded!"
        super().__init__(
            list,
            default=default,
            **kwargs
        )

    def update_keys(self) -> Tuple:
        return (self.name, f"add_{self.name}", f"remove_{self.name}")

    def update_value(self, instance, key: str, value) -> None:
        if key == self.name:
            setattr(instance, self.name, value.split(LIST_FIELD_SEPARATOR))
        else:
            current_value = getattr(instance, self.name)
            if key.startswith('add_'):
                value = current_value + value
            elif key.startswith('remove_'):
                value = list(set(current_value) - set(value))
            setattr(instance, self.name, value)

    def __set__(self, instance, value) -> None:
        if isinstance(value, str):
            value = value.split(LIST_FIELD_SEPARATOR)
        return super().__set__(instance, value)


class DictField(AbstractField):

    __slots__ = ()

    def __init__(self, default=None, **kwargs) -> None:
        if default is None:
            default = dict
        assert not kwargs.get('secondary_index', None), "Currently this is not supported by orm and query builded!"
        super().__init__(
            dict,
            default=default,
            **kwargs
        )

    def update_value(self, instance, _key: str, value) -> None:
        raise NotYetImplementException("Update value is currenty not implemented for dicts")

    @functools.lru_cache(None)
    def _query_row(self, model_instance) -> QueryRow:
        return DictQueryRow(self.name, model_ref=model_instance)


class JsonField(AbstractField):

    __slots__ = ()

    def __init__(self, default=None, **kwargs) -> None:
        if default is None:
            default = None
        assert not kwargs.get('secondary_index', None), "Currently this is not supported by orm and query builded!"
        super().__init__(
            (dict, list),
            default=default,
            **kwargs
        )

    def update_value(self, instance, _key: str, value) -> None:
        raise NotYetImplementException("Update value is currenty not implemented for dicts")

    @functools.lru_cache(None)
    def _query_row(self, model_instance) -> QueryRow:
        return DictQueryRow(self.name, model_ref=model_instance)
