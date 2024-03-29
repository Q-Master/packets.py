# -*- coding:utf-8 -*-
from typing import Union, Iterable
from . import FieldProcessor, SubPacket
from ._types import SubElementTyping
from .._packetbase import PacketBase


__all__ = ['Set']


class Set(FieldProcessor):
    """Set of elements processor"""

    @property
    def zero_value(self):
        return set()

    def __init__(self, element_type: SubElementTyping):
        """Constructor

        Args:
            element_type (Union[FieldProcessor, PacketBase]): type of the elements of the set.

        Raises:
            TypeError: if other than FieldProcessor or PacketBase ancestors given.
        """        
        super(Set, self).__init__()
        if isinstance(element_type, FieldProcessor):
            self._element_type = element_type
        elif issubclass(element_type, PacketBase):
            self._element_type = SubPacket(element_type)
        else:
            raise TypeError(f'element_type must be either FieldType or Packet ({type(element_type)})')

    def check_py(self, value: Union[list, tuple, set]):
        assert isinstance(value, (list, tuple, set)), (value, type(value))
        assert len(set(value)) == len(value), f'not a unique list of values in {value}'

    def check_raw(self, value: Union[list, tuple]):
        assert isinstance(value, (list, tuple)), (value, type(value))

    def raw_to_py(self, raw_sequence: Iterable, strict: bool) -> set:
        return {self._element_type.raw_to_py(value, strict) for value in raw_sequence}

    def py_to_raw(self, sequence: set) -> list:
        return [self._element_type.py_to_raw(value) for value in sequence]

    def dump_partial(self, sequence) -> list:
        return [self._element_type.dump_partial(value) for value in sequence]

    @property
    def my_type(self):
        return f'Set[{self._element_type.my_type}]'
