# -*- coding:utf-8 -*-
from typing import Type, Self, Dict, Any, Generic, Optional, cast, List, Union, Set, TypeVar, overload
import types, sys
from ._packetbase import PacketBase, PacketMeta
from ._types import DiffKeys, UpdateData
from .processors.subpacket import Subpacket, PT
from .processors.base import TypeDef
from .processors.hash import Hash, HashT
from .typedef.string_t import string_t


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
    def with_fields(cls, *field_names: str, recurse: bool = False) -> Type[Self]:
        fields_set = set(field_names) # raw names!!!
        cls_fields_set = set(cls.__raw_mapping__.keys()) # raw names !!!
        if recurse:
            fields_set &= cls_fields_set
        elif len(fields_set&cls_fields_set) != len(fields_set):
            raise TypeError(f'Failed to prepare packet. Unknown fields: {fields_set-(fields_set&cls_fields_set)}')
        normal_naming = {cls.__raw_mapping__[raw_name] for raw_name in fields_set }
        reconstructed_bases = []
        to_remove = set()
        need_recostruct = not recurse
        # need to check all bases to `with_fields` it
        for base in cls.__bases__:
            if issubclass(base, Packet):
                if base.has_field(normal_naming):
                    reconstructed_bases.append(base.with_fields(*fields_set, recurse=True))
                    for f in normal_naming:
                        if f in base.__local_fields_names__:
                            to_remove.add(f)
                    need_recostruct |= True
                else:
                    reconstructed_bases.append(base.with_fields(recurse=True))
                    need_recostruct |= True
            else:
                reconstructed_bases.append(base)
        if need_recostruct:
            normal_naming = normal_naming - to_remove
            namespace: dict[str, Any] = {field_name: cls.__fields__[field_name].clone() for field_name in normal_naming}
            partial_class: Type[Self] = types.new_class(f'Partial{cls.__name__}', tuple(reconstructed_bases), exec_body=lambda ns: ns.update(namespace))
            setattr(sys.modules[cls.__module__], f'_{cls.__name__}', partial_class)
            partial_class.__module__ = cls.__module__
            partial_class.__qualname__ = f'_{cls.__name__}'
        else:
            partial_class = cls
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


_TPTV = TypeVar('_TPTV', bound=Union[PacketBase, Any])


class TablePacketMeta(PacketMeta):
    def __new__(cls, cls_name, bases, namespace):
        df = namespace.get('__default_field__') # here should come TypeDef[T] or PacketBase or None for bases
        if df and not isinstance(df, (TypeDef, PacketBase, PacketMeta)):
            raise AttributeError(f'TablePacket "{cls_name}" __default_field__ is mandatory and must be a processor, but it is {type(df)}')
        if df:
            if isinstance(df, TypeDef):
                assert isinstance(df, TypeDef)
                _df = df
            else:
                _df = Subpacket[_TPTV](df) # type: ignore
            namespace['__default_field__'] = _df
            namespace['__table_packet_data__typedef__'] = Hash(string_t, _df)
        return PacketMeta.__new__(cls, cls_name, bases, namespace)


class TablePacket(PacketBase, Generic[_TPTV], metaclass = TablePacketMeta):
    """Same as a normal packet, but intended to use with initially unknown amount of rows.

    __default_field__ must be defined to show the structure of a row.
    """
    __default_field__: Optional[TypeDef[_TPTV]] = None
    __table_packet_data__: HashT[str, _TPTV] = HashT()
    __table_packet_data__typedef__: Hash[str, _TPTV]
    
    def __init__(self, __strict__=True, **kwargs) -> None:
        self.__table_packet_data__ = HashT()
        super().__init__(__strict__, **kwargs)
        self.__loading__ = True
        curr_fields = set(self.__class__.__fields__.keys())
        curr_fields.update(self.__class__.__raw_mapping__.keys())
        new_ones = set(kwargs.keys()) - curr_fields
        assert self.__class__.__default_field__ is not None
        try:
            for k in new_ones:
                r = kwargs.get(k, None)
                if r is not None:
                    self.__table_packet_data__[k] = self.__class__.__default_field__.py_to_py(r)
        except Exception as e:
            self.__loading__ = False
            raise ValueError(f'Failed to parse "{self.__class__.__name__}::{k}": {e}')
        self.__table_packet_data__.reset_modified()
        self.__loading__ = False
        self.__modified__ = False
        self.__parent__ = None

    def __repr__(self) -> str:
        pkt = ', '.join(
            f'{field_name}:{getattr(self, field_name)}' for field_name in self.__class__.__fields__.keys() if getattr(self, field_name) is not None
        )
        if self.__table_packet_data__:
            addon = ', '.join(f'{k}:{v}' for k, v in self.__table_packet_data__.items() if v is not None)
            if addon:
                pkt += f', {addon}'
        return f'{{{pkt}}}'

    def __iter__(self):
        for field_name in self.__class__.__fields__:
            yield getattr(self, field_name)
        for v in self.__table_packet_data__.values():
            yield v

    def __len__(self) -> int:
        return len(self.__fields__)+len(self.__table_packet_data__.keys())

    @classmethod
    def load(cls, raw_data, strict=True) -> Self:
        pkt = super().load(raw_data, strict)
        pkt.__table_packet_data__.reset_modified()
        return pkt

    def local_field_names(self) -> List[str]:
        result: List[str] = []
        result.extend(self.__class__.__local_fields_names__)
        result.extend(self.__table_packet_data__.keys())
        return result
    
    def field_names(self) -> List[str]:
        result: List[str] = []
        result.extend(self.__class__.__fields__.keys())
        result.extend(self.__table_packet_data__.keys())
        return result
    
    def field_raw_names(self) -> List[str]:
        result: List[str] = []
        result.extend(self.__class__.__raw_mapping__.keys())
        result.extend(self.__table_packet_data__.keys())
        return result
    
    def has_field(self, item: Union[str, List[str], Set[str]]):
        if isinstance(item, str):
            result = item in self.__class__.__fields__.keys() or item in self.__table_packet_data__.keys()
        else:
            result = len(set(item)&set(self.__class__.__fields__.keys())&set(self.__table_packet_data__.keys())) > 0
        return result

    def is_modified(self) -> bool:
        return super().is_modified() or self.__table_packet_data__.is_modified()
    
    def set_modified(self):
        self.__table_packet_data__.set_modified()
        super().set_modified()

    def set_ro(self, ro: bool):
        self.__table_packet_data__.set_ro(ro)
        super().set_ro(ro)

    def update_partial(self, update_data: UpdateData) -> None:
        curr_fields = set(self.__class__.__fields__.keys())
        curr_fields.update(self.__class__.__raw_mapping__.keys())
        new_ones = set(update_data.keys()) - curr_fields
        super().update_partial(UpdateData({k:v for k,v in update_data.items() if k in curr_fields}))
        self.__table_packet_data__typedef__.update_partial(self.__table_packet_data__, UpdateData({k:v for k,v in update_data.items() if k in new_ones}))

    def dump(self, raw=True) -> Dict[str, Any]:
        result = super().dump(raw)
        assert self.__default_field__ is not None
        result.update({k : self.__default_field__.py_to_raw(cast(_TPTV, v)) for k, v in self.__table_packet_data__.items() if v is not None})
        return result

    def dump_partial(self, field_paths: DiffKeys) -> Dict[str, Any]:
        curr_fields = set(self.__class__.__fields__.keys())
        curr_fields.update(self.__class__.__raw_mapping__.keys())
        new_ones = set(field_paths.keys()) - curr_fields
        result = super().dump_partial({k: v for k,v in field_paths if k in curr_fields})
        result.update(self.__table_packet_data__typedef__.dump_partial({k: v for k, v in field_paths.items() if k in new_ones}, self.__table_packet_data__))
        return result

    def packet_fields(self):
        for field_name in self.__class__.__fields__:
            yield (field_name, getattr(self, field_name))
        for k_v in self.__table_packet_data__.items():
            yield k_v

    def __getattr__(self, name) -> _TPTV:
        return self.__table_packet_data__[name]

    def __setattr__(self, name: str, value: _TPTV) -> None:
        has_attr = name in self.__fields__.keys() or name in dir(self)
        if has_attr:
            super().__setattr__(name, value)
        else:
            self.__table_packet_data__[name] = value

    def _parse_raw(self, raw_js, strict=True, update=False):
        super()._parse_raw(raw_js, strict)
        curr_fields = set(self.__class__.__fields__.keys())
        curr_fields.update(self.__class__.__raw_mapping__.keys())
        new_ones = set(raw_js.keys()) - curr_fields
        assert self.__default_field__ is not None
        try:
            for k in new_ones:
                r = raw_js.get(k, None)
                if r is None and update:
                    continue
                self.__table_packet_data__[k] = self.__default_field__.raw_to_py(r, strict)
        except Exception as e:
            self.__loading__ = False
            raise ValueError(f'Failed to parse "{self.__class__.__name__}::{k}": {e}')

    def diff_keys(self) -> DiffKeys:
        result = super().diff_keys()
        if self.__table_packet_data__.is_modified():
            hdiff = self.__table_packet_data__typedef__.diff_keys(self.__table_packet_data__)
            if hdiff:
                result.update(hdiff)
        return result

    def _raw_name_to_name(self, raw_name: str) -> str:
        return self.__class__.__raw_mapping__.get(raw_name, raw_name)


@overload
def makeDefaultField(processor: TypeDef[_TPTV]) -> TypeDef[_TPTV]: ...

@overload
def makeDefaultField(processor: Type[PT]) -> TypeDef[PT]: ...

def makeDefaultField(processor: Union[TypeDef[_TPTV], Type[PT]]) -> Union[TypeDef[_TPTV], TypeDef[PT]]:
    if isinstance(processor, TypeDef):
        return processor
    else:
        return cast(TypeDef[PT], processor)
