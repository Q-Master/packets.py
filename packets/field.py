# -*- coding:utf-8 -*-
from copy import deepcopy
from ._fieldinfo import FieldInfo, _not_set
from .processors import Const
from ._packetbase import FieldBase


__all__ = ['Field']


class Field(FieldBase):
    __instances_created = 0

    def __new__(cls, *args, **kwargs):
        instance = object.__new__(cls)
        cls.__instances_created += 1
        instance.__number = cls.__instances_created
        return instance

    def __init__(self, processor=_not_set, name=_not_set, default=_not_set, required=_not_set, override=_not_set):
        """Packet field constructor

        Args:
            processor (FieldProcessor, optional): field type processor. Defaults to _not_set.
            name (str, optional): serialized field name. Defaults to _not_set.
            default (Any, optional): default field value. Defaults to _not_set.
            required (bool, optional): flag if the field is required. Defaults to _not_set.
            override (bool, optional): flag if the field is overloaded. Defaults to _not_set.
        """        
        self._info = FieldInfo(processor, name, default, required, override)

    def __cmp__(self, other):
        return ((self.__number > other.__number) - (self.__number < other.__number))

    @property
    def info(self):
        return self._info

    def on_packet_class_create(self, parent_field, field_name):
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
            self._info.processor.check_raw(raw_value)
            py_value = self._info.processor.raw_to_py(raw_value, strict)

        if self._info.required and py_value is None:
            if not strict:
                py_value = self._info.processor.zero_value
            else:
                raise ValueError(f'Field required {self}')
        return py_value

    def py_to_raw(self, py_value):
        if py_value is None:
            if self._info.py_default is None:
                raw_value = None
            else:
                raw_value = deepcopy(self._info.default)
        else:
            self._info.processor.check_py(py_value)
            raw_value = self._info.processor.py_to_raw(py_value)

        if self._info.required and raw_value is None:
            raise ValueError(f'Field required {self}')
        return raw_value

    def clone(self, **kwargs):
        new_info = self._info.copy()
        new_info.update_params(kwargs)
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
        field.on_packet_class_create(self, self._info.py_name)
        return field

    def dump_partial(self, value):
        return self._info.processor.dump_partial(value)
    
    def __str__(self):
        return f'<{self.__class__.__name__}("{self._info.py_name}", "{self._info.name}")>'
