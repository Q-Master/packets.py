# -*- coding: utf8 -*-
from typing import TypeVar, Optional, Union, Type, Self
from .base import TypeDef


__all__ = ['Number', 'Percent', 'NumberAsString']


T=TypeVar('T', bound=Union[int, float])


class Number(TypeDef[T]):
    def __init__(self, typ: type[T], min: Optional[T] = None, max: Optional[T] = None) -> None:
        super().__init__()
        self._typ = typ
        self._min = min
        self._max = max
    
    def check_py(self, v: T) -> bool:
        if not isinstance(v, (int, float)):
            return False
        if self._min is not None and self._typ(v) < self._min:
            return False
        if self._max is not None and self._typ(v) > self._max:
            return False
        return True
    
    def check_raw(self, r) -> bool:
        if not isinstance(r, (int, float)):
            return False
        if self._min is not None and self._typ(r) < self._min:
            return False
        if self._max is not None and self._typ(r) > self._max:
            return False
        return True
    
    def raw_to_py(self, r, strict=True) -> T:
        return self._typ(r)

    def py_to_raw(self, v: T) -> T:
        return v

    def zero_value(self) -> T:
        return self._typ(0)

    def self_type(self) -> Type[T]:
        return self._typ

    def clone(self) -> Self:
        c = self.__class__(self._typ, self._min, self._max)
        c.set_ro(False)
        return c



class Percent(Number[float]):
    def raw_to_py(self, r, strict=True) -> float:
        res =  super().raw_to_py(r)
        return res/100.0

    def py_to_raw(self, v: float) -> float:
        return super().py_to_raw(v) * 100.0


class NumberAsString(Number[T]):
    def check_raw(self, r: str) -> bool:
        if not isinstance(r, str):
            return False
        try:
            raw = self._typ(float(r))
        except Exception:
            return False
        return super().check_raw(raw)

    def raw_to_py(self, r: str, strict=True) -> T:
        return super().raw_to_py(float(r))
    
    def py_to_raw(self, v: T) -> str:
        return f'{v}'
