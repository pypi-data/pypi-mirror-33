import base64
import os
from typing import Union


__all__ = [
    'set_int', 'set_float', 'set_bool', 'set_str', 'set_bytes', 'set_list', 'set',
]


def set_int(key: str, value: int, **_):
    os.environ[key] = str(value)


def set_float(key: str, value: float, **_):
    os.environ[key] = str(value)


def set_str(key: str, value: str, **_):
    os.environ[key] = value


def set_bool(key: str, value: bool, **_):
    os.environ[key] = '1' if value else '0'


def set_bytes(key: str, value: bytes, **_):
    os.environ[key] = base64.b64encode(value).decode()


def set_list(key: str, value: list, **kwargs):
    separator = kwargs.pop('separator', ',')
    serializer = kwargs.pop('serializer', str)
    os.environ[key] = separator.join(map(serializer, value))


def set(key: str, value: Union[int, float, bool, str, bytes, list], **kwargs):
    setters_map = {
        int: set_int,
        float: set_float,
        str: set_str,
        bool: set_bool,
        bytes: set_bytes,
        list: set_list,
    }
    value_type = type(value)
    if value_type in setters_map:
        setter = setters_map[value_type]
        setter(key, value, **kwargs)
    else:
        raise ValueError('Unknown value type')
