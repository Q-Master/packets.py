# -*- coding:utf-8 -*-
from typing import TypeAlias
from ..processors.base import TypeDef


class Bytes(TypeDef[bytes]):
    def check_py(self, v: bytes) -> bool:
        return isinstance(v, bytes)
    
    def check_raw(self, r: bytes) -> bool:
        return isinstance(r, bytes)
    
    def raw_to_py(self, r: bytes, strict=True) -> bytes:
        return r

    def py_to_raw(self, v: bytes) -> bytes:
        return v

    def zero_value(self) -> bytes:
        return b''

    def self_type(self) -> type[bytes]:
        return bytes


bytes_t = Bytes()
BytesT: TypeAlias = bytes
