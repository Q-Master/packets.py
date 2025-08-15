from abc import ABCMeta, abstractmethod
from ._fieldinfo import FieldInfo


__all__ = ['FieldBase']


class FieldBase(metaclass=ABCMeta):
    @abstractmethod
    def on_packet_class_create(self, parent_field, field_name):
        pass
    
    @abstractmethod
    def raw_to_py(self, raw_value, strict):
        pass
    
    @abstractmethod
    def py_to_raw(self, py_value):
        pass

    @property
    @abstractmethod
    def info(self) -> FieldInfo:
        pass

    @property
    @abstractmethod
    def name(self) -> str | None:
        pass

    @abstractmethod
    def clone(self, **kwargs):
        pass

    @abstractmethod
    def dump_partial(self, value):
        pass
