# -*- coding:utf-8 -*-
from typing import TypeVar, Generic
from collections.abc import Mapping, MutableMapping
from ._types import SubElementTyping
from .subpacket import SubPacket
from .numeric import Number, NumberAsString
from .date import UnixTime, UnixtimeAsString
from .string import String
from .enumeration import Enumeration, EnumerationByName
from .._packetbase import PacketBase
from .._fieldprocessorbase import FieldProcessor


__all__ = ['Hash']

K = TypeVar('K', Number, NumberAsString, UnixTime, UnixtimeAsString, String, Enumeration, EnumerationByName)
V = TypeVar('V', bound=SubElementTyping)


class Hash(Generic[K, V], FieldProcessor):
    """Dict processor"""
    @property
    def zero_value(self):
        return {}

    def __init__(self, key_type: K, element_type: V):
        if isinstance(key_type, FieldProcessor):
            if isinstance(key_type, Number):
                self._key_type = key_type.to_number_as_string()
            else:
                self._key_type = key_type
        else:
            raise TypeError(f'key_type must be FieldType, got {type(element_type)}')
        
        if isinstance(element_type, FieldProcessor):
            self._element_type = element_type
        elif issubclass(element_type, PacketBase):
            self._element_type = SubPacket(element_type)
        else:
            raise TypeError(f'element_type must be FieldType or Packet, got {type(element_type)}')

    def check_py(self, value):
        assert isinstance(value, (Mapping, MutableMapping)), (value, type(value))

    def check_raw(self, raw_value):
        assert isinstance(raw_value, (Mapping, MutableMapping)), (raw_value, type(raw_value))

    def raw_to_py(self, mapping: Mapping | MutableMapping, strict: bool) -> dict:
        result = {
            self._key_type.raw_to_py(key, strict): self._element_type.raw_to_py(value, strict)
            for key, value in mapping.items()
        }
        return result

    def py_to_raw(self, mapping: Mapping | MutableMapping) -> dict:
        return {
            self._key_type.py_to_raw(key): self._element_type.py_to_raw(value)
            for key, value in mapping.items()
        }

    def dump_partial(self, value: Mapping) -> dict:
        return {
            self._key_type.py_to_raw(key): self._element_type.dump_partial(value)
            for key, value in value.items()
        }

    @property
    def my_type(self):
        return Mapping[self._key_type.my_type, self._element_type.my_type]
