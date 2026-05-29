# -*- coding:utf-8 -*-
from typing import TYPE_CHECKING, Union, TypeVar, Type, List, Dict, Any, Self, Optional
import pickle
from . import json
from ._types import DiffKeys, UpdateData
if TYPE_CHECKING:
    from .field import Field


class PacketMeta(type):
    def __new__(cls, cls_name, bases, namespace):
        fields = {}
        rm = {}
        for base in bases:
            if hasattr(base, '__fields__'):
                fields.update(base.__fields__)
                rm.update(base.__raw_mapping__)
        namespace['__fields__'] = fields
        namespace['__raw_mapping__'] = rm
        return super().__new__(cls, cls_name, bases, namespace)


T = TypeVar('T', bound='PacketBase')


class PacketBase(metaclass=PacketMeta):
    __fields__: dict[str, 'Field'] = {}
    __local_fields_names__: List[str] = []
    __raw_mapping__: Dict[str, str] = {}
    __modified__: bool
    __loading__: bool
    __no_optionals__: bool = False
    __parent__: 'Optional[PacketBase]' = None

    def __init__(self, __strict__=True, **kwargs) -> None:
        """Constructor
        Constructor kwargs must have python values for fields, not raw values.
        For raw values loading use `load` or `update`.

        Args:
            __strict__ (bool, optional): true if need checking for required fields. Defaults to True.

        Raises:
            ValueError: Raised if field setting is impossible by some reason
        """
        self.has_modified = True
        self.__loading__ = True
        for field_name, field_processor in self.__fields__.items():
            r = kwargs.get(field_name, None)
            try:
                v = field_processor.py_to_py(r, __strict__)
            except Exception as e:
                self.__loading__ = False
                raise ValueError(f'Failed to parse "{self.__class__.__name__}::{field_name}": {e}')
            setattr(self, field_name, v)
        self.__loading__ = False
        self.__modified__ = False

    def __repr__(self) -> str:
        pkt = ', '.join(
            f'{field_name}:{getattr(self, field_name)}' for field_name in self.field_names() if getattr(self, field_name) is not None
        )
        return f'{{{pkt}}}'
    
    def __eq__(self, other: Self) -> bool:
        if isinstance(other, PacketBase):
            if self.__class__ != other.__class__:
                return False
            if self.field_names() != other.field_names():
                return False
            for py_name in self.field_names():
                if getattr(self, py_name) != getattr(other, py_name):
                    return False
            return True
        return False

    def __ne__(self, other: Self) -> bool:
        return not self == other
    
    def __setstate__(self, state):
        """Set state after Pickle deserialization

        Args:
            state (dict): restored state
        """
        self.__dict__.update(state) # type: ignore
        self.__modified__ = False

    def __getstate__(self) -> object:
        return self.__dict__.copy()

    def __iter__(self):
        for field_name in self.__class__.__fields__:
            yield getattr(self, field_name)

    def __deepcopy__(self, memo) -> Self:
        return pickle.loads(pickle.dumps(self, protocol=-1))

    def __len__(self) -> int:
        return len(self.__fields__)
    
    @classmethod
    def local_field_names(cls) -> List[str]:
        return cls.__local_fields_names__
    
    @classmethod
    def field_names(cls):
        return cls.__fields__.keys()
    
    @classmethod
    def field_raw_names(cls):
        return cls.__raw_mapping__.keys()
    
    @property
    def loading(self) -> bool:
        return self.__loading__

    def is_modified(self) -> bool:
        return self.__modified__
    
    def set_modified(self):
        self.__modified__ = True
        if self.__parent__:
            self.__parent__.set_modified()

    def no_optionals(self):
        return self.__no_optionals__

    @classmethod
    def set_ro(cls, ro: bool):
        for field in cls.__fields__.values():
            field.set_ro(ro)

    @classmethod
    def load(cls: Type[T], raw_data, strict=True) -> T:
        """Load packet from iterable (dict, list, etc...)

        Args:
            raw_data (dict | list | iterable): data to load to packet fields
            strict (bool, optional): whether to raise on required fields missing. Defaults to True.

        Returns:
            T: loaded packet
        """
        pckt = cls(__strict__=False)
        pckt.__loading__ = True
        try:
            pckt._parse_raw(raw_data, strict)
        finally:
            pckt.__loading__ = False
        pckt.on_packet_loaded()
        return pckt

    @classmethod
    def loadz(cls: Type[T], s: bytes) -> T:
        """Load packet from zip packed source string

        Returns:
            PacketBase[T]: loaded packet
        """        
        return cls.load(json.loads(s.decode('zip')))

    @classmethod
    def loads(cls: Type[T], s: str, strict=True) -> T:
        return cls.load(json.loads(s), strict)

    def update(self, raw_data):
        self._parse_raw(raw_data, update=True)
        self.on_packet_loaded()

    def update_partial(self, update_data: UpdateData) -> None:
        for rk, rv in update_data.items():
            k = self._raw_name_to_name(rk)
            field = self.__fields__[k]
            if isinstance(rv, UpdateData):
                #passthrough
                if not hasattr(self, k):
                    data = field.zero_value()
                    setattr(self, k, data)
                else:
                    data = getattr(self, k)
                if isinstance(data, PacketBase):
                    data.update_partial(rv)
                else:
                    field.update_partial(data, rv)
            else:
                setattr(self, k, field.raw_to_py(rv))

    def dump(self, raw=True) -> Dict[str, Any]:
        result = {}
        for field_name, field in self.__fields__.items():
            raw_value = field.py_to_raw(getattr(self, field_name))
            if raw_value is not None or field.may_be_none:
                result[field.name if raw else field_name] = raw_value
        return result

    def dump_partial(self, field_paths: DiffKeys) -> Dict[str, Any]:
        result = {}
        for raw_fn, subpaths in field_paths.items():
            fn = self._raw_name_to_name(raw_fn)
            field = self.__fields__.get(fn, None)
            if field:
                if isinstance(subpaths, str):
                    raw_value = field.py_to_raw(getattr(self, fn))
                    if raw_value is not None or field.may_be_none:
                        result[field.name] = raw_value
                else:
                    v = getattr(self, fn)
                    if isinstance(v, PacketBase):
                        result[field.name] = v.dump_partial(subpaths)
                    else:
                        result[field.name] = field.dump_partial(subpaths, v)
        return result

    def dumpz(self) -> bytes:
        """Serialize packet to zipped bytes

        Returns:
            str: serialized packet
        """        
        return json.dumps(self.dump()).encode('zip')

    def dumps(self, **kwargs) -> str:
        """Serialize packet to string

        Returns:
            str: serialized packet
        """        
        return json.dumps(self.dump(), **kwargs)

    def packet_fields(self):
        for field_name in self.__class__.__fields__:
            yield (field_name, getattr(self, field_name))

    def get(self, field_name: str, default=None):
        if field_name in self.field_names():
            return getattr(self, field_name)
        else:
            return default

    def get_by_raw(self, raw_field_name: str, default=None):
        if raw_field_name in self.field_raw_names():
            fn = self._raw_name_to_name(raw_field_name)
            return getattr(self, fn)
        else:
            return default

    def set_by_raw(self, raw_field_name: str, value: Any):
        if raw_field_name in self.field_raw_names():
            fn = self._raw_name_to_name(raw_field_name)
            setattr(self, fn, value)
        else:
            raise AttributeError(f'{self.__class__.__name__} has no RAW field name {raw_field_name}')

    def get_by_any(self, some_field_name: str, default=None):
        if some_field_name in self.field_raw_names():
            fn = self._raw_name_to_name(some_field_name)
            return getattr(self, fn)
        elif some_field_name in self.field_names():
            return getattr(self, some_field_name)
        else:
            return default

    def set_by_any(self, some_field_name: str, value: Any):
        if some_field_name in self.field_raw_names():
            fn = self._raw_name_to_name(some_field_name)
            setattr(self, fn, value)
        elif some_field_name in self.field_names():
            setattr(self, some_field_name, value)
        else:
            raise AttributeError(f'{self.__class__.__name__} has no field name {some_field_name}')

    def clone(self) -> Self:
        return pickle.loads(pickle.dumps(self, -1))

    def on_packet_loaded(self):
        """Callback on packet load or update.
        Need to be implemented in children if needed.
        """        
        pass

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

    def diff_keys(self) -> DiffKeys:
        res = {}
        if self.__modified__:
            for f in self.__fields__.values():
                v = f.diff_keys(self)
                if v is None:
                    continue
                res[f.name] = v
        return res

    def toDict(self) -> Union[dict, list, type[None]]:
        return self.dump()

    def _raw_name_to_name(self, raw_name: str) -> str:
        return self.__class__.__raw_mapping__[raw_name]
