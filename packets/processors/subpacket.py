# -*- coding:utf-8 -*-
from typing import Type
from collections.abc import Mapping
from .._packetbase import PacketBase
from ._base import FieldProcessor


__all__ = ['SubPacket']


class SubPacket(FieldProcessor):
    """Processor for underlying packets"""
    has_flat_value = True

    @property
    def zero_value(self):
        return self._packet_type(__strict=False)

    @property
    def packet_type(self):
        return self._packet_type

    def __init__(self, packet: Type[PacketBase]):
        """Constructor

        Args:
            packet (Type[PacketBase]): type of the subpacket
        """        
        assert issubclass(packet, PacketBase)
        self._packet_type = packet

    def check_py(self, py_value):
        assert isinstance(py_value, self._packet_type), (py_value, type(py_value), self._packet_type)

    def check_raw(self, raw_value):
        pass

    def raw_to_py(self, raw_value, strict) -> PacketBase:
        return self._packet_type.load(raw_value, strict)

    def py_to_raw(self, value: PacketBase) -> dict:
        return value.dump()

    def dump_partial(self, value):
        fields = self._packet_type.__fields__
        if isinstance(value, Mapping):
            return {
                fields[field_name].name: fields[field_name].dump_partial(value)
                for field_name, value in value.items()
                if field_name in fields
            }
        else:
            return super(SubPacket, self).dump_partial(value)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self._packet_type}>'
