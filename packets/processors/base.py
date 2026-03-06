# -*- coding:utf-8 -*-
from typing import TypeVar, Type, Generic, Self
from abc import ABCMeta, abstractmethod


__all__ = ['TypeDef']


T = TypeVar('T')


class TypeDef(Generic[T], metaclass=ABCMeta):
    def __init__(self) -> None:
        self._ro = False
    
    @abstractmethod
    def check_py(self, v: T) -> bool: ...

    @abstractmethod
    def check_raw(self, r) -> bool: ...

    @abstractmethod
    def raw_to_py(self, r, strict=True) -> T: ...
    
    @abstractmethod
    def py_to_raw(self, v: T) -> T: ...
    
    def py_to_py(self, v: T) -> T:
        return v
    
    @abstractmethod
    def zero_value(self) -> T: ...

    def is_const(self) -> bool:
        return self._ro
    
    def set_ro(self, ro: bool):
        self._ro = ro
    
    def clone(self) -> Self:
        c = self.__class__()
        c.set_ro(False)
        return c

    @abstractmethod
    def self_type(self) -> Type[T]: ...

    def diff_keys(self, data: T) -> str:
        return '1'
