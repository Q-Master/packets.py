# -*- coding:utf-8 -*-
from .processors import FieldProcessor, SubPacket
from ._packetbase import PacketBase, PacketMeta


__all__ = ['FieldInfo']


_not_set = object()


def is_set(x) -> bool:
    return x is not _not_set


class FieldInfo():
    processor = _not_set
    name = _not_set
    py_name = _not_set
    default = _not_set
    py_default = None
    required = _not_set
    override = _not_set
    min = _not_set
    max = _not_set
    mutable = True

    def _checkset_processor(self, processor):
        if isinstance(processor, FieldProcessor):
            self.processor = processor
        elif isinstance(processor, (PacketMeta,PacketBase)):
            self.processor = SubPacket(processor)
        else:
            raise TypeError(f'wrong processor: {type(processor)}')

    def __init__(self, processor=_not_set, name=_not_set, default=_not_set, required=_not_set, override=_not_set) -> None:
        if processor is not _not_set:
            self._checkset_processor(processor)
        if self.processor is None:
            raise TypeError(f'wrong processor: {type(processor)}')
        if name is not _not_set:
            self.name = name
        if default is not _not_set:
            self.default = default
        if required is not _not_set:
            self.required = required
        if override is not _not_set:
            self.override = override

    def copy(self) -> 'FieldInfo':
        fi = FieldInfo(processor=self.processor, name=self.name, default=self.default, required=self.required, override=self.override)
        fi.py_name = self.py_name
        fi.py_default = self.py_default
        fi.min = self.min
        fi.max = self.max
        fi.mutable = self.mutable
        return fi

    def update_params(self, processor=_not_set, name=_not_set, py_name=_not_set, default=_not_set, required=_not_set, override=_not_set):
        if processor is not _not_set:
            self._checkset_processor(processor)
        if self.processor is None:
            raise TypeError(f'wrong processor: {type(processor)}')
        if name is not _not_set:
            self.name = name
        if py_name is not _not_set:
            self.py_name = py_name
        if default is not _not_set:
            self.default = default
        if required is not _not_set:
            self.required = required
        if override is not _not_set:
            self.override = override

    def update(self, f_info: 'FieldInfo'):
        self.update_params(f_info.processor, f_info.name, f_info.py_name, f_info.default, f_info.required, f_info.override)

    def update_name(self, name):
        self.py_name = name
        if self.name is _not_set:
            self.name = name
    
    def set_defaults(self, default, required, override):
        if self.default is _not_set:
            self.default = default
        if self.default is None:
            self.py_default = None
        else:
            self.processor.check_raw(self.default)
            self.py_default = self.processor.raw_to_py(self.default, strict=True)
        if self.required is _not_set:
            self.required = required
        if self.override is _not_set:
            self.override = override
        if hasattr(self.processor, 'max'):
            self.max = self.processor.max
        if hasattr(self.processor, 'min'):
            self.min = self.processor.min
        self.mutable = self.processor.has_mutable_value

    def __str__(self) -> str:
        return f'''{{
    processor: {"not set" if self.processor is _not_set else type(self.processor)}
    name: {"not set" if self.name is _not_set else self.name}
    py_name: {"not set" if self.py_name is _not_set else self.py_name}
    default: {"not set" if self.default is _not_set else self.default}
    required: {"not set" if self.required is _not_set else self.required}
    override: {"not set" if self.override is _not_set else self.override}
    min: {"not set" if self.min is _not_set else self.min}
    max: {"not set" if self.max is _not_set else self.max}
    mutable: {"not set" if self.mutable is _not_set else self.mutable}
}}'''
