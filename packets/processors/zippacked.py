# -*- coding:utf-8 -*-
from .subpacket import SubPacket
from ._types import SubElementTyping
from .._packetbase import PacketBase
from .._fieldprocessorbase import FieldProcessor
from .. import json


__all__ = ['ZipPacked']


class ZipPacked(FieldProcessor):
    """Processor for fields packed with zip"""
    
    def __init__(self, element_type: SubElementTyping):
        """Constructor

        Args:
            element_type (Union[FieldProcessor, PacketBase]): type of the element of the zip.

        Raises:
            TypeError: if other than FieldProcessor or PacketBase ancestors given.
        """        
        super().__init__()
        if isinstance(element_type, FieldProcessor):
            self._element_type = element_type
        elif issubclass(element_type, PacketBase):
            self._element_type = SubPacket(element_type)
        else:
            raise TypeError(f'element_type must be either FieldType or Packet ({type(element_type)})')

    def check_raw(self, raw_value: bytes):
        assert isinstance(raw_value, bytes), (raw_value, type(raw_value))
        pass

    def check_py(self, py_value):
        self._element_type.check_py(py_value)
        pass

    def raw_to_py(self, raw_value: bytearray, strict):
        decoded = json.loads(raw_value.decode('zip'))
        return self._element_type.raw_to_py(decoded, strict)

    def py_to_raw(self, value) -> bytes:
        value = self._element_type.py_to_raw(value)
        return json.dumps(value).encode('zip')

    @property
    def my_type(self):
        return f'{self._element_type.my_type}'
