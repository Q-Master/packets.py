# -*- coding:utf-8 -*-
from typing import Optional
from ._fieldprocessorbase import FieldProcessor


__all__ = ['FieldInfo']


_not_set = object


def is_set(x) -> bool:
    return x is not _not_set


class FieldInfo():
    processor: Optional[FieldProcessor] = None 
    name: Optional[str] = None
    py_name: Optional[str] = None
    default = _not_set
    py_default = None
    required: Optional[bool] = None
    override: Optional[bool] = None
    min = _not_set
    max = _not_set
    mutable = True

    @property
    def my_type(self):
        if self.processor is None:
            raise RuntimeError('Field processor cant be None')
        if self.required or is_set(self.default):
            return self.processor.my_type
        else:
            return Optional[self.processor.my_type]

    @property
    def is_override(self) -> bool:
        return self.override if self.override is not None else False
    
    def __init__(self, 
        processor: Optional[FieldProcessor] = None, 
        name: Optional[str] = None, 
        default=_not_set, 
        required: Optional[bool] = None, 
        override: Optional[bool] = None
    ) -> None:
        if processor is not None:
            self.processor = processor
        if name is not None:
            self.name = name
        if default is not _not_set:
            self.default = default
        if required is not None:
            self.required = required
        if override is not None:
            self.override = override

    def copy(self) -> 'FieldInfo':
        fi = FieldInfo(processor=self.processor, name=self.name, default=self.default, required=self.required, override=self.override)
        fi.py_name = self.py_name
        fi.py_default = self.py_default
        fi.min = self.min
        fi.max = self.max
        fi.mutable = self.mutable
        return fi

    def update_params(self, 
        processor: Optional[FieldProcessor] = None, 
        name: Optional[str] = None, 
        py_name: Optional[str] = None, 
        default=_not_set, 
        required: Optional[bool] = None, 
        override: Optional[bool] = None
    ):
        if processor is not None:
            self.processor = processor
        if name is not None:
            self.name = name
        if py_name is not None:
            self.py_name = py_name
        if default is not _not_set:
            self.default = default
        if required is not None:
            self.required = required
        if override is not None:
            self.override = override

    def update(self, f_info: 'FieldInfo'):
        self.update_params(f_info.processor, f_info.name, f_info.py_name, f_info.default, f_info.required, f_info.override)

    def update_name(self, name: str):
        self.py_name = name
        if self.name is None:
            self.name = name
    
    def set_defaults(self, default, required: bool, override: bool):
        if self.default is _not_set:
            self.default = default
        if self.default is None:
            self.py_default = None
        else:
            if self.processor:
                self.processor.check_raw(self.default)
                self.py_default = self.processor.raw_to_py(self.default, strict=True)
                if hasattr(self.processor, 'max'):
                    self.max = self.processor.max # type: ignore
                if hasattr(self.processor, 'min'):
                    self.min = self.processor.min # type: ignore
                self.mutable = self.processor.has_mutable_value
        if self.required is None:
            self.required = required
        if self.override is None:
            self.override = override

    def has_default(self) -> bool:
        return is_set(self.default)

    def __str__(self) -> str:
        return f'''{{
    processor: {"not set" if self.processor is None else type(self.processor)}
    name: {"not set" if self.name is None else self.name}
    py_name: {"not set" if self.py_name is None else self.py_name}
    default: {"not set" if self.default is _not_set else self.default}
    required: {"not set" if self.required is None else self.required}
    override: {"not set" if self.override is None else self.override}
    min: {"not set" if self.min is _not_set else self.min}
    max: {"not set" if self.max is _not_set else self.max}
    mutable: {"not set" if self.mutable is _not_set else self.mutable}
    }}'''
