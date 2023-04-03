# -*- coding:utf-8 -*-
from numbers import Integral
from collections.abc import Sequence
from ._base import FieldProcessor
from .subpacket import SubPacket
from .._packetbase import PacketBase
from ._types import StringTypes, SubElementTyping


__all__ = ['Array']


class Array(FieldProcessor):
    """Simple array processor"""

    @property
    def zero_value(self):
        if not self._length:
            return []
        else:
            return [self._element_type.zero_value for _ in range(self._length)]

    @property
    def element_type(self):
        return self._element_type

    @property
    def length(self):
        return self._length

    def __init__(self, element_type: SubElementTyping, length=None):
        super(Array, self).__init__()
        assert isinstance(length, (type(None), Integral)), (length, type(length))
        if isinstance(element_type, FieldProcessor):
            self._element_type = element_type
        elif issubclass(element_type, PacketBase):
            self._element_type = SubPacket(element_type)
        else:
            raise TypeError(f'Array element must be either field processor or Packet not {type(element_type)}')
        self._length = length

    def check_py(self, value):
        assert isinstance(value, Sequence), (value, type(value))
        assert not isinstance(value, StringTypes), (value, type(value))
        if self._length is not None and len(value) != self._length:
            raise ValueError(f'Wrong array length {len(value)}({self._length})')

    def check_raw(self, value):
        assert isinstance(value, Sequence), (value, type(value))
        assert not isinstance(value, StringTypes), (value, type(value))
        if self._length is not None and len(value) != self._length:
            raise ValueError(f'Wrong array length {len(value)}({self._length})')

    def raw_to_py(self, raw_sequence, strict) -> list:
        return [self._element_type.raw_to_py(value, strict) for value in raw_sequence]

    def py_to_raw(self, sequence: Sequence):
        return [self._element_type.py_to_raw(value) for value in sequence]

    def dump_partial(self, sequence: Sequence) -> list:
        return [self._element_type.dump_partial(value) for value in sequence]

    @property
    def my_type(self):
        return f'List[{self._element_type.my_type}]'
