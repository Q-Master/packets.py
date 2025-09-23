# -*- coding:utf-8 -*-
from typing import List, Optional, Type, Self, TYPE_CHECKING, TypeVar, cast, MutableMapping, Union
import zlib
import types
from itertools import groupby
from ._packetbase import PacketBase, DiffKeys
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
            if field.name in raw_js.keys():
                raw_value = raw_js.get(field.name, None)
                try:
                    field_value = field.raw_to_py(raw_value, strict=strict)
                except Exception as e:
                    raise ValueError(f'Failed to parse "{cls.__name__}::{field_name}": {e}')
                attrs[field_name] = field_value
        return attrs

    def dump(self, raw=True) -> dict:
        js_dict = {}
        for field_name, field in self.__fields__.items():
            raw_value = field.py_to_raw(getattr(self, field_name))
            if raw_value is not None:
                js_dict[field.name if raw else field_name] = raw_value
        return js_dict

    def dump_partial(self, field_paths: DiffKeys) -> dict:
        result = {}
        for fn, subpaths in field_paths.items():
            field = self.__fields__.get(fn, None)
            if field:
                if isinstance(subpaths, str):
                    raw_value = field.py_to_raw(getattr(self, fn))
                    if raw_value is not None:
                        result[field.name] = raw_value
                else:
                    result[field.name] = getattr(self, fn).dump_partial(subpaths)
        return result


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
            try:
                field_value = field.raw_to_py(raw_value, strict=strict)
            except Exception as e:
                raise ValueError(f'Failed to parse "{cls.__name__}::{field_name}": {e}')
            attrs[field_name] = field_value
        return attrs

    def dump(self):
        return [field.py_to_raw(getattr(self, field_name)) for field_name, field in self.__fields__.items()]

    def dump_partial(self, field_paths: DiffKeys):
        return self.dump()

    def __iter__(self):
        for field_name in self.__fields__:
            yield getattr(self, field_name)


TPT = TypeVar('TPT', bound=PacketBase)

class TablePacket(Packet, MutableMapping[str, TPT]):
    """Same as a normal packet, but intended to use with initially unknown amount of rows.

    __default_field__ must be defined to show the structure of a row.
    """
    __default_field__: Optional[TPT] = None

    @classmethod
    def load(cls, raw_data, strict=True):
        if not cls.__default_field__:
            raise AttributeError(u'DefaultPacket must have default field')
        curr_fields = set(cls.__fields__.keys())
        curr_fields.update(cls.__raw_mapping__.keys())
        namespace = {k: v for k, v in cls.__dict__.items() if k not in curr_fields}
        namespace.update({fieldname: field.clone(override=False) for fieldname, field in cls.__fields__.items()})
        namespace.update({'__default_field__': cast(Field, cls.__default_field__).clone(override=False)})
        partial_class: Type[Self] = types.new_class(cls.__name__, cls.__bases__, exec_body=lambda ns: ns.update(namespace))
        new_fields = set(raw_data.keys())
        new_ones = new_fields - curr_fields
        for k in raw_data.keys():
            if k not in new_ones:
                continue
            nm = k
            assert partial_class.__default_field__ is not None
            new_field = cast(Field, partial_class.__default_field__).clone(name=k, override=True)
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
        for new in raw_data.keys():
            if new not in new_ones:
                continue
            nm = new
            assert self.__class__.__default_field__ is not None
            new_field = cast(Field, self.__class__.__default_field__).clone(name=new, override=True)
            self.__class__.__fields__[nm] = new_field
            new_field.on_packet_class_create(new_field, new)
            self.__class__.__raw_mapping__[nm] = new
        super().update(raw_data)

    def __len__(self) -> int:
        return len(self.__fields__)
    
    if TYPE_CHECKING:
        def __getattr__(self, name: str) -> TPT:
            cls = super().__getattribute__('__class__')
            if name not in cls.__fields__:
                df = super().__getattribute__('__default_field__')
                assert df is not None
                return df
            raise AttributeError()
