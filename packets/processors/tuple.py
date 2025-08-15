# -*- coding:utf-8 -*-
from typing import Iterable, Tuple as TypingTuple, List
from ._types import SubElementTyping
from .subpacket import SubPacket
from .._packetbase import PacketBase
from .._fieldprocessorbase import FieldProcessor


__all__ = ['Tuple']


class Tuple(FieldProcessor):
    """Tuple of elements"""
    has_flat_value = True

    @property
    def zero_value(self):
        return tuple(et.zero_value for et in self._element_types)

    def __init__(self, *element_types: SubElementTyping):        
        """Constructor

        Args:
            element_types (tuple[Union[FieldProcessor, PacketBase]]): type of the elements of the tuple.

        Raises:
            TypeError: if other than FieldProcessor or PacketBase ancestors given.
        """        
        self._element_types: List[FieldProcessor] = []
        for element_type in element_types:
            if isinstance(element_type, FieldProcessor):
                self._element_types.append(element_type)
            elif issubclass(element_type, PacketBase):
                self._element_types.append(SubPacket(element_type))
            else:
                raise TypeError(f'element_type must be either FieldType or Packet ({type(element_type)})')
        self._length = len(self._element_types)

    def check_py(self, py_value):
        assert isinstance(py_value, (list, tuple)), (py_value, type(py_value))
        if len(py_value) != self._length:
            raise ValueError(f'Not enough elements in list for tuple {len(py_value)} ({self._length})')
        for processor, value in zip(self._element_types, py_value):
            processor.check_py(value)

    def check_raw(self, raw_value):
        assert isinstance(raw_value, (list, tuple)), (raw_value, type(raw_value))
        if len(raw_value) != self._length:
            raise ValueError(f'Not enough elements in list for tuple {len(raw_value)} ({self._length})')

    def raw_to_py(self, raw_sequence: Iterable, strict) -> tuple:
        return tuple(t.raw_to_py(v, strict) for v, t in zip(raw_sequence, self._element_types))

    def py_to_raw(self, sequence: Iterable) -> tuple:
        return tuple(t.py_to_raw(v) for v, t in zip(sequence, self._element_types))

    def dump_partial(self, sequence):
        return tuple(t.dump_partial(v) for v, t in zip(sequence, self._element_types))

    @property
    def my_type(self):
        alltypes = [x.my_type for x in self._element_types]
        return TypingTuple[*alltypes]
