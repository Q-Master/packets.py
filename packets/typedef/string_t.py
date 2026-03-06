# -*- coding:utf-8 -*-
from typing import Optional, TypeAlias, Self
from ..processors.base import TypeDef


class String(TypeDef[str]):
    def __init__(self, max_length: Optional[int]=None, trim=False) -> None:
        super().__init__()
        self._max_length = max_length
        self._trim = trim

    def check_py(self, v: str) -> bool:
        res = isinstance(v, (str))
        res |= not self._trim and self._max_length is not None and len(v) > self._max_length
        return res
    
    def check_raw(self, r) -> bool:
        res = isinstance(r, (str))
        res |= not self._trim and self._max_length is not None and len(r) > self._max_length
        return res
    
    def raw_to_py(self, r, strict=True) -> str:
        if self._trim and self._max_length:
            return str(r)[0:self._max_length]
        else:
            return str(r)

    def py_to_raw(self, v: str) -> str:
        if self._trim and self._max_length:
            return str(v)[0:self._max_length]
        else:
            return str(v)

    def zero_value(self) -> str:
        return ''

    def self_type(self) -> type[str]:
        return str

    def clone(self) -> Self:
        c = self.__class__(self._max_length, self._trim)
        c.set_ro(False)
        return c

string_t = String()
StringT: TypeAlias = str
