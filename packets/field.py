# -*- coding:utf-8 -*-
from typing import Generic, TypeVar, TYPE_CHECKING, Union, Optional, Any, overload, Type, Self, Literal
from copy import deepcopy
from ._types import DiffKeys
from .processors.base import TypeDef
from .processors import Subpacket
if TYPE_CHECKING:
    from ._packetbase import PacketBase


class _not_set():
    pass


FT = TypeVar('FT')


class Field(Generic[FT]):
    def __init__(self, typ: TypeDef[FT], name: Optional[str] = None, default: Union[FT, None, type[_not_set]] = _not_set, required: bool = False, override: bool = False) -> None:
        self._typ = typ.clone()
        self.name: str = name # type: ignore
        #default value is ALWAYS raw value, so need to convert to Python value
        if default is _not_set or default is None:
            self._default_value = default 
        else:
            if not self._typ.check_raw(default):
                raise ValueError(f'RAW default {default} ({type(default)}) is not valid')
            self._default_value = self._typ.raw_to_py(default, strict=False)
        self._instance_name = ''
        self._instance_modified_name = ''
        self._required = required
        self._override = override
        #print(f'INIT {self.__class__.__name__}')

    def __set__(self, instance: 'PacketBase', value: FT):
        #print(f'Set {self._name} to {value}')
        if self._typ._ro and not instance.__loading__:
            #print(f'Not setting {instance.__class__.__name__}::{self.name}. CONST')
            return
        if __debug__:
            if self._required and value is not None:
                assert self._typ.check_py(value), f'Value {value} of {type(value)} is not valid'
        value = self._typ.py_to_py(value)
        if self._typ.has_modified and value is not None:
            value.__parent__ = instance # type: ignore
            if not instance.__loading__:
                value.set_modified() # type: ignore
        if not instance.__loading__:
            setattr(instance, self._instance_name, value)
            setattr(instance, self._instance_modified_name, True)
            instance.set_modified()
        else:
            if value is not None:
                setattr(instance, self._instance_name, value)

    @overload
    def __get__(self, instance: None, owner = None) -> Self:...

    @overload
    def __get__(self, instance: 'PacketBase', owner = None) -> FT:...

    def __get__(self, instance: 'Union[PacketBase, None]', owner = None) -> Union[FT, Self, None]:
        if instance is None:
            return self
        if hasattr(instance, self._instance_name):
            return getattr(instance, self._instance_name)
        else:
            if self.has_default:
                dflt = self.default
                setattr(instance, self._instance_name, dflt)
                return dflt
            return None
    
    def __delete__(self, instance: 'PacketBase'):
        delattr(instance, self._instance_name)
        delattr(instance, self._instance_modified_name)
        instance.set_modified()

    def __set_name__(self, owner: 'PacketBase', name):
        if name == '__default_field__':
            return
        if self.name is None:
            self.name = name
        f = owner.__fields__.get(name, None)
        if f:
            if not self._override:
                raise TypeError(f'Repeated field "{owner.__name__}::{self.name}"')
            else:
                self.name = f.name
                self._instance_name = f._instance_name
                self._instance_modified_name = f._instance_modified_name
                self._required = f._required
        else:
            self._instance_name = f'_{name}'
            self._instance_modified_name = f'_{name}_modified'
        if owner.__no_optionals__ and (not self._required and not self.has_default):
            raise TypeError(f'Packet "{owner.__name__}" can not have optional field "{self.name}"')
        owner.__fields__[name] = self
        owner.__local_fields_names__.append(name)
        assert self.name is not None
        owner.__raw_mapping__[self.name] = name
        owner.__annotations__[self.name] = self._typ.self_type()
        #print(f'SET NAME to {self._name}')

    @property
    def required(self) -> bool:
        return self._required
    
    @property
    def override(self) -> bool:
        return self._override
    
    @property
    def has_default(self) -> bool:
        return self._default_value is not _not_set

    @property 
    def default(self) -> Optional[FT]:
        if self.has_default:
            return deepcopy(self._default_value) # type: ignore
        else:
            return None

    def is_modified(self, instance: 'PacketBase') -> bool:
        if self._typ.has_modified:
            return getattr(instance, self._instance_name).is_modified()
        return getattr(instance, self._instance_modified_name, False)
    
    def py_to_py(self, v: FT, strict=True) -> Optional[FT]:
        res: Optional[FT]
        if v is None:
            if self._required and strict and not self.has_default:
                raise ValueError(f'Field "{self.name}" required')
            else:
                res = None
        else:
            if __debug__:
                if not self._typ.check_py(v):
                    raise ValueError(f'Py value {v} ({type(v)}) is not valid')
            res = self._typ.py_to_py(v)
        if res is None and self._required and strict and not self.has_default:
            raise ValueError(f'Field "{self.name}" required')
        return res

    def raw_to_py(self, r, strict = True) -> Optional[FT]:
        if r is None:
            if self._required and strict:
                raise ValueError(f'Field "{self.name}" required')
            else:
                v = None
        else:
            if __debug__:
                if not self._typ.check_raw(r):
                    raise ValueError(f'RAW value {r} ({type(r)}) is not valid')
            v = self._typ.raw_to_py(r, strict)
        if v is None and self._required and strict:
            raise ValueError(f'Field "{self.name}" required')
        return v # type: ignore

    def py_to_raw(self, v: FT):
        if v is None:
            if self.default is None:
                r = None
            else:
                r = self._typ.py_to_raw(self._default_value) # type: ignore
        else:
            if __debug__:
                if not self._typ.check_py(v):
                    raise ValueError(f'Value {v} ({type(v)}) is not valid')
            r = self._typ.py_to_raw(v)
        
        if self._required and r is None:
            raise ValueError(f'Field required "{self.name}"')
        return r

    def clone(self) -> Self:
        return self.__class__(self._typ, self.name, self._default_value, self._required, self._override)

    def zero_value(self) -> FT:
        return self._typ.zero_value()
    
    def set_ro(self, ro: bool):
        self._typ.set_ro(ro)

    def diff_keys(self, instance: 'PacketBase') -> Optional[Union[str, None, DiffKeys]]:
        if self.is_modified(instance):
            data = getattr(instance, self._instance_name)
            return self._typ.diff_keys(data)
        return None




_PT = TypeVar('_PT', bound='PacketBase')


@overload
def makeField(processor: TypeDef[FT], name: Optional[str] = ..., default = _not_set, required: Literal[False] = False, override: bool = ...) -> Optional[FT]: ...

@overload
def makeField(processor: TypeDef[FT], name: Optional[str] = ..., default = _not_set, required: Literal[True] = True, override: bool = ...) -> FT: ...

@overload
def makeField(processor: TypeDef[FT], name: Optional[str] = ..., default: Union[Any, None] = ..., required: bool = ..., override: bool = ...) -> FT: ...

@overload
def makeField(processor: Type[_PT], name: Optional[str] = ..., default = _not_set, required: Literal[False] = False, override: bool = ...) -> Optional[_PT]: ...

@overload
def makeField(processor: Type[_PT], name: Optional[str] = ..., default = _not_set, required: Literal[True] = True, override: bool = ...) -> _PT: ...

@overload
def makeField(processor: Type[_PT], name: Optional[str] = ..., default: Union[Any, None] = ..., required: bool = ..., override: bool = ...) -> _PT: ...

def makeField(processor: Union[TypeDef[FT], Type[_PT]], name: Optional[str] = None, default: Union[Any, None, type[_not_set]] = _not_set, required: bool = False, override: bool = False) -> Any:
    if isinstance(processor, TypeDef):
        typ = processor.self_type()
        fld = Field[typ](processor, name, default, required, override)
        return fld
    else:
        proc: TypeDef[_PT] = Subpacket[_PT](processor)
        fld = Field[_PT](proc, name, default, required, override)
        return fld
