# -*- coding:utf-8 -*-
from typing import Type, Self, Dict, Any, Generic, TYPE_CHECKING, cast, List
import types
from ._packetbase import PacketBase, DiffKeys
from .field import Field
from .processors.subpacket import PT


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
    def _parse_raw(self, raw_js, strict=True, update=False):
        for field_name, field in self.__fields__.items():
            r = raw_js.get(field.name, None)
            if r is None and update:
                continue
            try:
                v = field.raw_to_py(r, strict=strict)
            except Exception as e:
                raise ValueError(f'Failed to parse "{self.__class__.__name__}::{field_name}": {e}')
            setattr(self, field_name, v)

    def dump(self, raw=True) -> Dict[str, Any]:
        result = {}
        for field_name, field in self.__fields__.items():
            raw_value = field.py_to_raw(getattr(self, field_name))
            if raw_value is not None:
                result[field.name if raw else field_name] = raw_value
        return result

    def dump_partial(self, field_paths: DiffKeys) -> Dict[str, Any]:
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

    @classmethod
    def with_fields(cls, *field_names: str) -> Type[Self]:
        fields_set = set(field_names) # raw names!!!
        cls_fields_set = set(cls.__raw_mapping__.keys()) # raw names !!!
        if len(fields_set&cls_fields_set) != len(fields_set):
            raise TypeError(f'Failed to prepare packet. Unknown fields: {fields_set-(fields_set&cls_fields_set)}')
        normal_naming = {raw_name: cls.__raw_mapping__[raw_name] for raw_name in fields_set }
        namespace: dict[str, Any] = {field_name: cls.__fields__[field_name].clone() for field_name in normal_naming.values()}
        partial_class: Type[Self] = types.new_class(f'Partial{cls.__name__}', (Packet, ), exec_body=lambda ns: ns.update(namespace))
        return partial_class


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
    __no_optionals__: bool = True
    def _parse_raw(self, raw_js_list, strict=True, update=False):
        for (field_name, field), r in zip(self.__fields__.items(), raw_js_list):
            try:
                v = field.raw_to_py(r, strict=strict)
            except Exception as e:
                raise ValueError(f'Failed to parse "{self.__class__.__name__}::{field_name}": {e}')
            setattr(self, field_name, v)
    
    def dump(self) -> List[Any]:
        return [field.py_to_raw(getattr(self, field_name)) for field_name, field in self.__fields__.items()]

    def dump_partial(self, field_paths: DiffKeys):
        return self.dump()


class TablePacket(Packet, Generic[PT]):
    """Same as a normal packet, but intended to use with initially unknown amount of rows.

    __default_field__ must be defined to show the structure of a row.
    """
    __default_field__: PT
    
    @classmethod
    def load(cls, raw_data, strict=True) -> Self:
        """Load packet from iterable (dict, list, etc...)

        Args:
            raw_data (dict | list | iterable): data to load to packet fields
            strict (bool, optional): whether to raise on required fields missing. Defaults to True.

        Returns:
            T: loaded packet
        """
        assert issubclass(cls, TablePacket)
        if cls.__dict__.get('__default_field__', None) is None:
            raise AttributeError(f'TablePacket "{cls.__name__}" __default_field__ is mandatory')
        curr_fields = set(cls.__fields__.keys())
        curr_fields.update(cls.__raw_mapping__.keys())
        new_fields = set(raw_data.keys())
        new_ones = new_fields - curr_fields
        namespace: Dict[str, Any] = {k: v for k, v in cls.__dict__.items()}
        for k in raw_data.keys():
            if k in new_ones:
                namespace[k] = cast(Field[PT], cls.__default_field__).clone()
        partial_class: Type[TablePacket[PT]] = types.new_class(f'PartialTable{cls.__name__}', cls.__bases__, exec_body = lambda ns: ns.clear() or ns.update(namespace))
        pckt = partial_class(__strict__=False)
        pckt.__loading__ = True
        try:
            pckt._parse_raw(raw_data, strict)
        finally:
            pckt.__loading__ = False
        pckt.on_packet_loaded()
        return cast(Self, pckt)


    def __reduce__(self) -> tuple[Any, ...]:
        ns = {k: v for k, v in self.__class__.__dict__.items() if isinstance(v, Field)}
        ns.update({
            '__fields__': self.__class__.__dict__['__fields__'],
            '__raw_mapping__': self.__class__.__dict__['__raw_mapping__']
        })
        return (
            create_table_packet_class,
            (self.__class__.__name__, self.__class__.__bases__, ns),
            self.__dict__
        )

    if TYPE_CHECKING:
        def __getattr__(self, name: str) -> PT:
            cls = super().__getattribute__('__class__')
            if name not in cls.__fields__:
                df = super().__getattribute__('__default_field__')
                assert df is not None
                return df
            raise AttributeError()


def create_table_packet_class(name, bases, namespace) -> TablePacket:
    partial_class = types.new_class(f'Partial{name}', bases, exec_body = lambda ns: ns.update(namespace))
    pckt = partial_class(__strict__=False)
    return pckt
