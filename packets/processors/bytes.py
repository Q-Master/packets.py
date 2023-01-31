# -*- coding:utf-8 -*-
from ._base import FieldProcessor


__all__ = ['Bytes', 'bytes_t']


class Bytes(FieldProcessor):
    """Processor for bytes type"""
    has_mutable_value = False
    zero_value = b''

    def __init__(self, strip=None):
        self._strip = strip

    def check_py(self, value):
        assert isinstance(value, bytes), (value, type(value))

    def check_raw(self, value):
        assert isinstance(value, str), (value, type(value))

    def raw_to_py(self, raw_value: str, strict) -> bytes:
        value = raw_value
        if self._strip is not None:
            value = value.strip(self._strip)
        return value.encode('utf-8')

    def py_to_raw(self, py_value: bytes) -> str:
        return py_value.decode('utf-8')

bytes_t = Bytes()
