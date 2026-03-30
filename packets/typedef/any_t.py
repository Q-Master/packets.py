# -*- coding:utf-8 -*-
from typing import TypeAlias, Any
from ..processors.base import TypeDef


class AnyD(TypeDef[object]):

    def check_py(self, v: Any) -> bool:
        return True
    
    def check_raw(self, r: Any) -> bool:
        return True
    
    def raw_to_py(self, r: Any, strict=True) -> Any:
        return r

    def py_to_raw(self, v: Any) -> Any:
        return v

    def zero_value(self) -> object:
        return None

    def self_type(self) -> type[object]:
        return object


any_t = AnyD()
AnyT: TypeAlias = Any
