# -*- coding:utf-8 -*-
from typing import Optional, Type, Any, overload, TypeVar, Literal, cast
from copy import deepcopy
from ._fieldinfo import FieldInfo, _not_set
from .processors import Const, SubPacket
from ._packetbase import PacketBase
from ._fieldbase import FieldBase
from ._fieldprocessorbase import FieldProcessor


__all__ = ['Field', 'makeField']


class Field(FieldBase):
    __instances_created: int = 0
    __number: int = 0
    _info: FieldInfo

    @property
    def info(self) -> FieldInfo:
        return self._info

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        cls.__instances_created += 1
        instance.__number = cls.__instances_created
        return instance

    def __init__(self, processor: Optional[FieldProcessor] | Type[PacketBase] = None, name: Optional[str] = None, default: Any = _not_set, required: Optional[bool] = None, override: Optional[bool] = None):
        """Packet field constructor

        Args:
            processor (FieldProcessor, optional): field type processor. Defaults to None.
            name (str, optional): serialized field name. Defaults to None.
            default (Any, optional): default field value. Defaults to _not_set.
            required (bool, optional): flag if the field is required. Defaults to None.
            override (bool, optional): flag if the field is overloaded. Defaults to None.
        """
        self._info = FieldInfo(self._fix_processor(processor), name, default, required, override)

    @property
    def name(self) -> str:
        assert self._info.name is not None
        return self._info.name


    def on_packet_class_create(self, parent_field: 'Field', field_name: str) -> None:
        """Callback to set field name on packet creation

        Args:
            parent_field (Field): parent field
            field_name (str): in-python field name
        """

        if parent_field is not None:
            if not self._info.override == True:
                raise TypeError(f'Repeated field {field_name}')
            else:
                new_info = parent_field._info.copy()
                new_info.update(self._info)
                self._info = new_info
        self._info.set_defaults(None, False, False)
        self._info.update_name(field_name)

    def raw_to_py(self, raw_value, strict):
        if raw_value is None:
            if self._info.py_default is None:
                py_value = None
            else:
                py_value = deepcopy(self._info.py_default)
        else:
            assert self._info.processor is not None
            self._info.processor.check_raw(raw_value)
            py_value = self._info.processor.raw_to_py(raw_value, strict)

        if self._info.required and py_value is None:
            if not strict:
                assert self._info.processor is not None
                py_value = self._info.processor.zero_value
            else:
                raise ValueError(f'Field required')
        return py_value

    def py_to_raw(self, py_value):
        if py_value is None:
            if self._info.py_default is None:
                raw_value = None
            else:
                raw_value = deepcopy(self._info.default)
        else:
            assert self._info.processor is not None
            self._info.processor.check_py(py_value)
            raw_value = self._info.processor.py_to_raw(py_value)

        if self._info.required and raw_value is None:
            raise ValueError(f'Field required {self}')
        return raw_value

    def clone(self, processor: Optional[FieldProcessor] | Type[PacketBase] = None, **kwargs):
        new_info = self._info.copy()
        new_info.update_params(self._fix_processor(processor), **kwargs)
        field = self.__class__()
        field._info = new_info
        return field

    def frozen_clone(self, value):
        field = self.__class__(
            Const(value),
            name=self._info.name,
            default=value,
            required=self._info.required,
            override=True
        )
        assert self._info.py_name is not None, 'Packet field name cant be None'
        field.on_packet_class_create(self, self._info.py_name)
        return field

    def dump_partial(self, value):
        assert self._info.processor is not None
        return self._info.processor.dump_partial(value)
    
    def __str__(self):
        return f'<{self.__class__.__name__}("{self._info.py_name}", "{self._info.name}")>'

    def __cmp__(self, other):
        return ((self.__number > other.__number) - (self.__number < other.__number))

    def _fix_processor(self, processor: Optional[FieldProcessor] | type[PacketBase]) -> Optional[FieldProcessor]:
        if isinstance(processor, FieldProcessor):
            return processor
        elif isinstance(processor, type(None)):
            return None
        elif issubclass(processor, PacketBase):
            return SubPacket(processor)
        else:
            raise TypeError(f'wrong processor: {type(processor)}')



_P = TypeVar('_P', bound=PacketBase)


@overload
def makeField(processor: Type[_P], name: Optional[str] = ..., default: Any | None | _not_set = ..., required: Literal[False] = False, override: Optional[bool] = ...) -> Optional[_P]: ...

@overload
def makeField(processor: Type[_P], name: Optional[str] = ..., default: Any | None | _not_set = ..., required: Literal[True] = True, override: Optional[bool] = ...) -> _P: ...


@overload
def makeField(processor: FieldProcessor, name: Optional[str] = ..., default: Any | None | _not_set = ..., required: Literal[True] = True, override: Optional[bool] = ...) -> Any: ...

@overload
def makeField(processor: FieldProcessor, name: Optional[str] = ..., default: Any | None | _not_set = ..., required: Literal[False] = False, override: Optional[bool] = ...) -> Optional[Any]: ...


@overload
def makeField(processor: Optional[FieldProcessor] | Type[PacketBase] = ..., name: Optional[str] = ..., default: Any | None | _not_set = ..., required: Literal[False] = False, override: Optional[bool] = ...) -> Optional[Any]: ...


def makeField(processor: Optional[FieldProcessor] | Type[PacketBase] = None, name: Optional[str] = None, default: Any | None | _not_set =_not_set, required: Optional[bool] = None, override: Optional[bool] = None) -> Any:
    fld = Field(processor, name, default, required, override)
    return fld
