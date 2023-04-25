# -*- coding:utf-8 -*-
from typing import Optional
import zlib
from ._packetbase import PacketBase
from .field import Field


__all__ = ['Packet', 'PacketWithID', 'ArrayPacket', 'TablePacket']


class Packet(PacketBase):
    """Normal packet.
    e.x.
    B:
        a: str

    A:
        a: int
        b: B
    Serializes to {a: int, b: {a: str}}
    """    
    @classmethod
    def _parse_raw(cls, raw_js, strict=True):
        attrs = {}
        for field_name, field in cls.__fields__.items():
            if field.info.name in raw_js.keys():
                raw_value = raw_js.get(field.info.name, None)
                field_value = field.raw_to_py(raw_value, strict=strict)
                attrs[field_name] = field_value
        return attrs

    def dump(self, raw=True):
        js_dict = {}
        for field_name, field in self.__fields__.items():
            raw_value = field.py_to_raw(getattr(self, field_name))
            if raw_value is not None:
                js_dict[field.info.name if raw else field_name] = raw_value
        return js_dict

    @classmethod
    def dump_partial(cls, partial_data):
        fields = cls.__fields__
        return {
            fields[field_name].name: fields[field_name].dump_partial(value)
            for field_name, value in partial_data.items()
            if field_name in fields and (value is not None or fields[field_name].required)
        }

    def __iter__(self):
        for field_name in self.__class__.__fields__:
            yield getattr(self, field_name)

    def packet_fields(self):
        for field_name in self.__class__.__fields__:
            yield (field_name, getattr(self, field_name))

    def keys(self):
        return self.__class__.__fields__.keys()


class PacketWithID(Packet):
    @classmethod
    def calc_packet_id(cls) -> int:
        packet_id = zlib.crc32(bytes('{}__{}'.format('__'.join([f'{base.__module__}__{base.__name__}' for base in cls.__bases__]), cls.__name__), 'utf-8'))
        if packet_id >= (1 << 31):
            packet_id = packet_id - (1 << 32)
        return packet_id


class ArrayPacket(PacketBase):
    """Packet represented as array.

    e.x.
    B:
        a: str
        b: float

    A:
        a: int
        b: B
    Serializes to [int, [str, float]]
    !!! Can't store optional fields.
    """    
    @classmethod
    def _parse_raw(cls, raw_list, strict=True):
        attrs = {}
        for (field_name, field), raw_value in zip(cls.__fields__.items(), raw_list):
            field_value = field.raw_to_py(raw_value, strict=strict)
            attrs[field_name] = field_value
        return attrs

    def dump(self):
        return [field.py_to_raw(getattr(self, field_name)) for field_name, field in self.__fields__.items()]

    def __iter__(self):
        for field_name in self.__fields__:
            yield getattr(self, field_name)


class TablePacket(Packet):
    """Same as a normal packet, but intended to use with initially unknown amount of rows.

    __default_field__ must be defined to show the structure of a row.
    """
    __default_field__: Optional[Field] = None

    @classmethod
    def load(cls, raw_data, strict=True):
        if not cls.__default_field__:
            raise AttributeError(u'DefaultPacket must have default field')
        curr_fields = set(cls.__fields__.keys())
        curr_fields.update(cls.__raw_mapping__.keys())
        namespace = {k: v for k, v in cls.__dict__.items() if k not in curr_fields}
        namespace.update({fieldname: field.clone(override=False) for fieldname, field in cls.__fields__.items()})
        namespace.update({'__default_field__': cls.__default_field__.clone(override=False)})
        partial_class = type(cls.__name__, cls.__bases__, namespace)
        new_fields = set(raw_data.keys())
        new_ones = new_fields - curr_fields
        for k in sorted(new_ones):
            nm = cls.__default_field__.name or k
            new_field = partial_class.__default_field__.clone(name=k, override=True)  # pylint: disable=no-member
            partial_class.__fields__[nm] = new_field
            new_field.on_packet_class_create(new_field, k)
            partial_class.__raw_mapping__[nm] = k
        return super(TablePacket, partial_class).load(raw_data, strict)

    def update(self, raw_data):
        curr_fields = set(self.__class__.__fields__.keys())
        curr_fields.update(self.__class__.__raw_mapping__.keys())
        new_fields = set(raw_data.keys())
        missing = curr_fields - new_fields
        new_ones = new_fields - curr_fields
        for item in missing:
            del self.__class__.__fields__[item]
            del self.__class__.__raw_mapping__[item]
            del self[item]
        for new in new_ones:
            nm = self.__class__.__default_field__.name or new
            new_field = self.__class__.__default_field__.clone(name=new, override=True)
            self.__class__.__fields__[nm] = new_field
            new_field.on_packet_class_create(new_field, new)
            self.__class__.__raw_mapping__[nm] = new
        super().update(raw_data)
