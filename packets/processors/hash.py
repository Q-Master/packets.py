# -*- coding:utf-8 -*-
from collections.abc import Mapping, MutableMapping
from .._packetbase import PacketBase
from . import FieldProcessor, SubPacket, Number
from ._types import BooleanType, SubElementTyping


__all__ = ['Hash']


class Hash(FieldProcessor):
    """Dict processor"""
    @property
    def zero_value(self):
        return {}

    def __init__(self, key_type: SubElementTyping, element_type: SubElementTyping):
        if isinstance(element_type, FieldProcessor):
            self._element_type = element_type
        elif issubclass(element_type, PacketBase):
            self._element_type = SubPacket(element_type)
        else:
            raise TypeError(f'element_type must be FieldType or Packet, got {type(element_type)}')

        if isinstance(key_type, FieldProcessor):
            if isinstance(key_type, Number):
                self._key_type = key_type.to_number_as_string()
            else:
                self._key_type = key_type
        elif issubclass(key_type, PacketBase):
            self._key_type = SubPacket(key_type)
        else:
            raise TypeError(f'key_type must be FieldType or Packet, got {type(element_type)}')

    def check_py(self, value):
        assert isinstance(value, Mapping), (value, type(value))

    def check_raw(self, raw_value):
        assert isinstance(raw_value, Mapping), (raw_value, type(raw_value))

    def raw_to_py(self, mapping: Mapping, strict: bool) -> dict:
        result = {
            self._key_type.raw_to_py(key, strict): self._element_type.raw_to_py(value, strict)
            for key, value in mapping.items()
        }
        return result

    def py_to_raw(self, mapping: Mapping) -> dict:
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
        return f'Dict[{self._key_type.my_type}, {self._element_type.my_type}]'
