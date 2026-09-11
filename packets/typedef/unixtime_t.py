# -*- coding:utf-8 -*-
from typing import Type, Union, TypeAlias
import time
from ..processors.base import TypeDef


UnixtimeT: TypeAlias = int


class Unixtime(TypeDef[UnixtimeT]):
    """Unixtime processor. Stores `unixtime` as int"""

    def check_py(self, v: UnixtimeT) -> bool:
        if v < 0 or v > 4294967295:
            return False
        return isinstance(v, UnixtimeT)
    
    def check_raw(self, r: Union[int, float]) -> bool:
        if r < 0 or r > 4294967295:
            return False
        return isinstance(r, (int, float))
    
    def raw_to_py(self, r: Union[int, float], strict=True) -> UnixtimeT:
        return UnixtimeT(r)

    def py_to_raw(self, v: UnixtimeT) -> int:
        return int(v)

    def zero_value(self) -> UnixtimeT:
        return int(time.time())

    def self_type(self) -> Type[UnixtimeT]:
        return UnixtimeT


class UnixtimeAsString(TypeDef[UnixtimeT]):
    """Unixtime processor. Stores `unixtime` as string using `self._date_format`"""

    def check_py(self, v: UnixtimeT) -> bool:
        if v < 0 or v > 4294967295:
            return False
        return isinstance(v, (int, float))
    
    def check_raw(self, r: str) -> bool:
        if float(r) < 0 or float(r) > 4294967295:
            return False
        return isinstance(r, str)
    
    def raw_to_py(self, r: str, strict=True) -> UnixtimeT:
        return UnixtimeT(float(r))

    def py_to_raw(self, v: UnixtimeT) -> str:
        return str(int(v))

    def zero_value(self) -> UnixtimeT:
        return UnixtimeT(time.time())

    def self_type(self) -> Type[UnixtimeT]:
        return UnixtimeT



unixtime_t = Unixtime()
unixtime_ts = UnixtimeAsString()
