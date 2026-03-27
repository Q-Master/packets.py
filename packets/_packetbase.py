# -*- coding:utf-8 -*-
from typing import TYPE_CHECKING, Union, TypeVar, Type, List, Dict, Any, TypeAlias, Self, Optional
import pickle
from abc import ABCMeta, abstractmethod
from . import json
from ._types import DiffKeys
if TYPE_CHECKING:
    from .field import Field


class PacketMeta(ABCMeta):
    def __new__(cls, cls_name, bases, namespace):
        fields = {}
        rm = {}
        for base in bases:
            if hasattr(base, '__fields__'):
                fields = base.__fields__.copy()
                rm = base.__raw_mapping__.copy()
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

    def update_partial(self, field_pairs: Dict[str, Any]) -> None:
        for k, v in field_pairs.items():
            setattr(self, k, v)

    @abstractmethod
    def dump(self) -> Union[dict, list, type[None]]:
        """Required interface method for packet serialization
        """        
        pass

    @abstractmethod
    def dump_partial(self, field_paths: DiffKeys):
        pass

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

    def clone(self) -> Self:
        return pickle.loads(pickle.dumps(self, -1))

    def on_packet_loaded(self):
        """Callback on packet load or update.
        Need to be implemented in children if needed.
        """        
        pass

    @abstractmethod
    def _parse_raw(self, raw_data, strict=True, update=False):
        """Parse raw dict data and set it to self

        Args:
            raw_data (dict, list): raw json data
            strict (bool, optional): option to ignore required fields. Defaults to True.
        """
        pass

    def diff_keys(self) -> DiffKeys:
        res = {}
        if self.__modified__:
            for k, f in self.__fields__.items():
                v = f.diff_keys(self)
                if v is None:
                    continue
                res[k] = v
        return res
