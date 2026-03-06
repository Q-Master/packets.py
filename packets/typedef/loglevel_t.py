# -*- coding:utf-8 -*-
from typing import TypeAlias
from logging import _levelToName, _nameToLevel, DEBUG
from ..processors.base import TypeDef


class Loglevel(TypeDef[int]):
    def check_py(self, v: int) -> bool:
        return v in _levelToName.keys()
    
    def check_raw(self, r: str) -> bool:
        return r.upper() in _nameToLevel.keys()
    
    def raw_to_py(self, r: str, strict=True) -> int:
        return _nameToLevel[r.upper()]

    def py_to_raw(self, v: int) -> str:
        return _levelToName[v]

    def zero_value(self) -> int:
        return DEBUG

    def self_type(self) -> type[int]:
        return int


loglevel_t = Loglevel()
LoglevelT: TypeAlias = int
