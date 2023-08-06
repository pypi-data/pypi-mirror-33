import asyncio
import logging
from enum import Enum
from importlib import import_module
from typing import Any, Dict, Callable, Tuple, Sequence, Type

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.7"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"

__all__ = [
    'process_functions', 'prettify_value', 'NotYetImplementException',
    'ensure_element', 'ensure_sequence', 'ensure_dict', 'merge_dicts',
    "import_class"
]

_log = logging.getLogger(__name__)


class NotYetImplementException(Exception):
    """
    Exception that caused when you use some function or method than not yet implemented for this part of functionallity and exists
    only to implement abstract classes
    """


def process_functions(fields_dict: Dict, init_function: Callable, configure_function: Callable, definer_ignore: bool = False) -> Tuple[Callable, Callable]:
    for key, value in sorted(fields_dict.items(), key=lambda x: x[0]):
        # Skip service values
        if value.service:
            continue
        # To keep compatibility for cases when we use fields without model
        # for example, like service configuration for cartridges
        if value.name is None:
            value.name = key
        if not (value.definer and definer_ignore):
            init_function = value.wrap_function_with_parameter(
                init_function,
                required=not value.optional,
                use_default=True
            )
        if value.reconfigurable or (value.definer and not definer_ignore):
            configure_function = value.wrap_function_with_parameter(
                configure_function,
                required=not value.reconfigurable,
                use_default=False
            )
    return init_function, configure_function


def prettify_value(value) -> Any:
    if isinstance(value, Enum):
        return value.name
    if isinstance(value, list):
        return [prettify_value(x) for x in value]
    if isinstance(value, tuple):
        return tuple(prettify_value(x) for x in value)
    if isinstance(value, dict):
        return {prettify_value(k): prettify_value(v) for k, v in value.items()}
    return value


async def ensure_element(element):
    if isinstance(element, asyncio.Future):
        return await element
    if isinstance(element, (list, tuple)):
        return await ensure_sequence(element)
    if isinstance(element, dict):
        await ensure_dict(element)
    return element


async def ensure_sequence(sequence: Sequence) -> Sequence:
    return [await ensure_element(x) for x in sequence]


async def ensure_dict(model_dict: Dict) -> Dict:
    for key, value in model_dict.items():
        if isinstance(value, asyncio.Future):
            model_dict[key] = await value
        if isinstance(value, dict):
            await ensure_dict(value)
        if isinstance(value, (list, tuple)):
            model_dict[key] = await ensure_sequence(value)
    return model_dict


def merge_dicts(source, destination):
    """
    run me with nosetests --with-doctest file.py

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge_dicts(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True

    Copied from: https://stackoverflow.com/questions/20656135/python-deep-merge-dictionary-data
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge_dicts(value, node)
        else:
            destination[key] = value

    return destination


def import_class(class_path: str) -> Type:
    module_path, class_name = class_path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, class_name, None)
