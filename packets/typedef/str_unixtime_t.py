# -*- coding:utf-8 -*-
from typing import Type, TypeAlias
import time
from ..processors.base import TypeDef
from .unixtime_t import UnixtimeT


StrUnixtimeT: TypeAlias = UnixtimeT


class UnixtimeAsString(TypeDef[StrUnixtimeT]):
    """Unixtime processor. Stores `unixtime` as string using `self._date_format`"""

    def check_py(self, v: StrUnixtimeT) -> bool:
        if v < 0 or v > 4294967295:
            return False
        return isinstance(v, (int, float))
    
    def check_raw(self, r: str) -> bool:
        if float(r) < 0 or float(r) > 4294967295:
            return False
        return isinstance(r, str)
    
    def raw_to_py(self, r: str, strict=True) -> StrUnixtimeT:
        return StrUnixtimeT(float(r))

    def py_to_raw(self, v: StrUnixtimeT) -> str:
        return str(int(v))

    def zero_value(self) -> StrUnixtimeT:
        return StrUnixtimeT(time.time())

    def self_type(self) -> Type[StrUnixtimeT]:
        return StrUnixtimeT


str_unixtime_t = UnixtimeAsString()
