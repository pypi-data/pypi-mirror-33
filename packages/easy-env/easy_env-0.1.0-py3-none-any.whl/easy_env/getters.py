import base64
import os
from typing import Callable, Optional, TypeVar, Union


__all__ = [
    'get_int', 'get_float', 'get_bool', 'get_str', 'get_bytes', 'get_list', 'get',
]
TRUE_VALUES = set('1 true t yes y ok okay confirm absolutely totally yep'.split())
FALSE_VALUES = set("0 false f no n bad nope don't".split())
T = TypeVar('T')


def process(factory: Callable[[str], T], key: str, default: Optional[T],
            raise_error: bool) -> Optional[T]:
    value = os.getenv(key, None)
    if value is None:
        if default is not None:
            value = default
        elif raise_error:
            raise KeyError('Failed to find env var {}'.format(key))
    else:
        value = factory(value)
    return value


def bool_factory(value: str) -> bool:
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    raise ValueError("Bad boolean value.")


def list_factory(value: str, separator: str, item_factory):
    return list(map(item_factory, value.split(separator)))


def get_int(key: str, default: Optional[int] = None, raise_error=False, **_) -> Optional[int]:
    return process(int, key, default, raise_error)


def get_float(key: str, default: Optional[float] = None, raise_error=False, **_) -> Optional[float]:
    return process(float, key, default, raise_error)


def get_str(key: str, default: Optional[str] = None, raise_error=False, **_) -> Optional[str]:
    return process(lambda x: str(x), key, default, raise_error)


def get_bool(key: str, default: Optional[bool] = None, raise_error=False, **_) -> Optional[bool]:
    return process(bool_factory, key, default, raise_error)


def get_bytes(key: str, default: Optional[bytes] = None, raise_error=False, **_) -> Optional[bytes]:
    return process(base64.b64decode, key, default, raise_error)


def get_list(key: str, default: Optional[list] = None, raise_error=False, **kwargs) -> Optional[list]:
    separator = kwargs.pop('separator', ',')
    item_factory = kwargs.pop('item_factory', str)
    return process(lambda x: list_factory(x, separator, item_factory),
                   key, default, raise_error)


def based_on_default(key: str, default: Optional[int] = None,
                     raise_error=False, **kwargs):
    type_mapper = {
        int: get_int,
        float: get_float,
        str: get_str,
        bool: get_bool,
        bytes: get_bytes,
        list: get_list,
    }
    default_type = type(default)
    if default_type in type_mapper:
        getter = type_mapper[default_type]
        return getter(key, default, raise_error, **kwargs)
    raise ValueError("Unknown type of default value.")


def get(key: str, default: Optional[Union[int, float, bool, str, bytes, list]] = None,
        raise_error=False, separator=',', item_factory=str, encoding='utf-8'):
    """Autodetect right type based on default."""
    if default is not None:
        return based_on_default(key, default, raise_error, separator=separator,
                                item_factory=item_factory, encoding=encoding)
    return get_str(key, default, raise_error)
