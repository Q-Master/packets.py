# -*- coding:utf-8 -*-
from typing import Type, TypeVar, Generic
from collections.abc import Mapping, MutableMapping
from .._packetbase import PacketBase
from .._fieldprocessorbase import FieldProcessor


__all__ = ['SubPacket']


T = TypeVar('T', bound=PacketBase)


class SubPacket(Generic[T], FieldProcessor):
    """Processor for underlying packets"""
    has_flat_value = True
    _packet_type: Type[T]

    @property
    def zero_value(self):
        return self._packet_type(__strict=False)

    @property
    def packet_type(self):
        return self._packet_type

    def __init__(self, packet: Type[T]):
        """Constructor

        Args:
            packet (Type[PacketBase]): type of the subpacket
        """        
        assert issubclass(packet, PacketBase)
        self._packet_type = packet

    def check_py(self, py_value: T):
        assert isinstance(py_value, self._packet_type), (py_value, type(py_value), self._packet_type)

    def check_raw(self, raw_value):
        pass

    def raw_to_py(self, raw_value: Mapping | MutableMapping, strict) -> T:
        return self._packet_type.load(raw_value, strict)

    def py_to_raw(self, value: T) -> dict | None:
        return value.dump()

    def dump_partial(self, value: Mapping | MutableMapping):
        fields = self._packet_type.__fields__
        if isinstance(value, (Mapping, MutableMapping)):
            return {
                fields[field_name].name: fields[field_name].dump_partial(value)
                for field_name, value in value.items()
                if field_name in fields
            }
        else:
            return super().dump_partial(value)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self._packet_type}>'

    @property
    def my_type(self):
        return self._packet_type
