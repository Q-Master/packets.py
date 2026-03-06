# -*- coding:utf-8 -*-
from typing import Type, Union, TypeVar, Self
from .base import TypeDef
from .._packetbase import PacketBase
from .._types import DiffKeys


__all__ = ['Subpacket']


PT = TypeVar('PT', bound='PacketBase', infer_variance=True)


class Subpacket(TypeDef[PT]):
    def __init__(self, typ: Type[PT]) -> None:
        super().__init__()
        self._typ = typ
    
    def check_py(self, v: PT) -> bool:
        return isinstance(v, PacketBase)

    def check_raw(self, r) -> bool:
        return isinstance(r, (dict, list))

    def raw_to_py(self, r: Union[list, dict], strict=True) -> PT:
        return self._typ.load(r, strict)

    def py_to_raw(self, v: PT) -> Union[list, dict, type[None]]:
        return v.dump()
    
    def self_type(self) -> Type[PT]:
        return self._typ

    def zero_value(self) -> PT:
        return self._typ(__strict=False)

    def set_ro(self, ro: bool):
        super().set_ro(ro)
        self._typ.set_ro(ro)

    def clone(self) -> Self:
        c = self.__class__(self._typ)
        c.set_ro(False)
        return c

    def diff_keys(self, data: PT) -> DiffKeys:
        return data.diff_keys()
