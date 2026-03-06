# -*- coding:utf-8 -*-
from typing import Generic, TypeVar, TYPE_CHECKING, Union, Optional, Any, overload, Type, Self, Literal
from copy import deepcopy
from ._types import DiffKeys
from .processors.base import TypeDef
from .processors import Subpacket, Hash, Set, Array
from .typedef.object_t import Object
if TYPE_CHECKING:
    from ._packetbase import PacketBase


class _not_set():
    pass


FT = TypeVar('FT')


class Field(Generic[FT]):
    def __init__(self, typ: TypeDef[FT], name: Optional[str] = None, default: Union[FT, None, type[_not_set]] = _not_set, required: bool = False, override: bool = False) -> None:
        self._typ = typ.clone()
        self._name = name
        self._default_value = default
        self._instance_name = ''
        self._instance_modified_name = ''
        self._required = required
        self._override = override
        #print(f'INIT {self.__class__.__name__}')

    def __set__(self, instance: 'PacketBase', value: FT):
        #print(f'Set {self._name} to {value}')
        if self._typ.is_const() and not instance.is_loading():
            #print(f'Not setting {instance.__class__.__name__}::{self.name}. CONST')
            return
        if self._required and value is not None:
            assert self._typ.check_py(value), f'Value {value} of {type(value)} is not valid'
        value = self._typ.py_to_py(value)
        setattr(instance, self._instance_name, value)
        has_modified = hasattr(value, 'set_modified')
        if has_modified:
            value.__parent__ = instance # type: ignore
            if not instance.is_loading():
                value.set_modified() # type: ignore
        if not instance.is_loading():
            setattr(instance, self._instance_modified_name, True)
            instance.set_modified()

    @overload
    def __get__(self, instance: None, owner = None) -> Self:...

    @overload
    def __get__(self, instance: 'PacketBase', owner = None) -> FT:...

    def __get__(self, instance: 'Union[PacketBase, None]', owner = None) -> Union[FT, Self, None]:
        if instance is None:
            return self
        try:
            return getattr(instance, self._instance_name)
        except AttributeError:
            return None
    
    def __delete__(self, instance: 'PacketBase'):
        delattr(instance, self._instance_name)
        delattr(instance, self._instance_modified_name)
        instance.set_modified()

    def __set_name__(self, owner: 'PacketBase', name):
        if name == '__default_field__':
            return
        if self._name is None:
            self._name = name
        f = owner.__fields__.get(name, None)
        if f:
            if not self._override:
                raise TypeError(f'Repeated field "{owner.__name__}::{self._name}"')
            else:
                self._name = f._name
                self._instance_name = f._instance_name
                self._instance_modified_name = f._instance_modified_name
                self._required = f._required
        if owner.__no_optionals__ and (not self._required and self._default_value is _not_set):
            raise TypeError(f'Packet "{owner.__name__}" can not have optional field "{self._name}"')
        self._instance_name = f'_{name}'
        self._instance_modified_name = f'_{name}_modified'
        owner.__fields__[name] = self
        owner.__local_fields_names__.append(name)
        assert self._name is not None
        owner.__raw_mapping__[self._name] = name
        #print(f'SET NAME to {self._name}')

    @property
    def name(self) -> str:
        return self._name # type: ignore

    @property
    def required(self) -> bool:
        return self._required
    
    @property
    def override(self) -> bool:
        return self._override
    
    @property
    def has_default(self) -> bool:
        return self._default_value is not _not_set

    def is_modified(self, instance: 'PacketBase') -> bool:
        if isinstance(self._typ, (Subpacket, Set, Hash, Array, Object)):
            return getattr(instance, self._instance_name).is_modified()
        return getattr(instance, self._instance_modified_name, False)
    
    def raw_to_py(self, r, strict = True) -> Optional[FT]:
        if r is None:
            if self._required and strict:
                raise ValueError(f'Field "{self._name}" required')
            if self._default_value is _not_set:
                v = None
            else:
                v = deepcopy(self._default_value)
        else:
            if not self._typ.check_raw(r):
                raise ValueError(f'RAW value {r} is not valid')
            v = self._typ.raw_to_py(r, strict)
        if v is None:
            if self._required and strict:
                raise ValueError(f'Field "{self._name}" required')
            else:
                return None
        return self._typ.raw_to_py(r, strict)

    def py_to_raw(self, v: FT):
        if v is None:
            if self._default_value is _not_set or self._default_value is None:
                r = None
            else:
                r = self._typ.py_to_raw(self._default_value) # type: ignore
        else:
            if not self._typ.check_py(v):
                raise ValueError(f'Value {v} is not valid')
            r = self._typ.py_to_raw(v)
        
        if self._required and r is None:
            raise ValueError(f'Field required "{self._name}"')
        return r

    def update_defaults(self, instance: 'PacketBase'):
        if self._default_value is not _not_set:
            setattr(instance, self._instance_name, deepcopy(self._default_value))

    def clone(self) -> Self:
        return self.__class__(self._typ, self._name, self._default_value, self._required, self._override)

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
