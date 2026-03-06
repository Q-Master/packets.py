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


unixtime_t = Unixtime()
