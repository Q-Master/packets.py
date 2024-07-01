# -*- coding:utf-8 -*-
from typing import Any, List
import pickle
from typing import Set, Dict, TypeVar, Type
from copy import deepcopy
from operator import itemgetter
from collections import Counter
from abc import ABCMeta, abstractmethod
from . import json


__all__ = ['PacketBase', 'FieldBase']


class FieldBase():
    pass


class PacketMeta(ABCMeta):
    def __new__(cls, cls_name, bases, namespace):
        fields = {}
        tags = set(namespace.get('packet_tags', []))

        for base in bases:
            if hasattr(base, '__fields__'):
                for field_name, field in base.__fields__.items():
                    if field_name != 'packet_id':
                        assert field_name not in fields, f'Repeated field {field_name} (class {base})'
                    fields[field_name] = field
            if hasattr(base, '__tags__'):
                tags.update(base.__tags__)
        not_inherited_fields = {
            field_name: field for field_name, field in namespace.items()
            if isinstance(field, FieldBase) and field_name != '__default_field__'
        }
        for field_name, field in sorted(not_inherited_fields.items(), key=itemgetter(0)):
            field.on_packet_class_create(fields.get(field_name), field_name)
            fields[field_name] = field
        for field_name, count in Counter(field.info.name for field in fields.values()).items():
            if count > 1:
                raise TypeError(f'Packet has two fields with same name: {field_name}')
        namespace['__fields__'] = fields
        namespace['__tags__'] = tags
        namespace['__raw_mapping__'] = {field.info.name: field.info.py_name for field_name, field in fields.items()}
        return super().__new__(cls, cls_name, bases, namespace)

T = TypeVar('T', bound='PacketBase')


class PacketBase(metaclass=PacketMeta):
    """Base class for packets"""
    
    __fields__: Dict[str, FieldBase] = {}
    __tags__: Set[str] = set()
    __raw_mapping__: Dict[str, str] = {}
    __modified = None

    def __repr__(self):
        return '<%s>' % (', '.join(
                ': '.join((field_name, str(getattr(self, field_name)))) for field_name in self.__fields__ if getattr(self, field_name) is not None
            )
        )

    @classmethod
    def fields_names(cls):
        """Returns list of field names

        Returns:
            List[str]: list of all field names used in that packet
        """        
        return cls.__fields__.keys()

    @classmethod
    def escaped_fields_names(cls):
        """Returns escaped list of field names

        Returns:
            List[str]: escaped list of all field names used in that packet
        """        
        return [f'"{key}"' for key in cls.__fields__.keys()]

    @classmethod
    def __subclasshook__(cls, other):
        try:
            other_mro = other.__mro__
            if PacketBase in other_mro:
                if any((cls.__name__ == x.__name__ for x in other_mro)):
                    return True
                if cls.__name__ == other.__name__:
                    return True
        except AttributeError:
            pass
        return NotImplemented

    def __init__(self, **kwargs):
        super().__init__()
        strict = kwargs.pop('__strict', True)
        for field_name, field_processor in self.__fields__.items():
            if field_name not in kwargs:
                value = field_processor.raw_to_py(None, strict=strict)
            else:
                value = kwargs.pop(field_name)
            setattr(self, field_name, value)
        self.__modified = False
        assert not kwargs, f'Extra arguments: {kwargs}'

    def __setstate__(self, state):
        """Set state after Pickle deserialization

        Args:
            state (dict): restored state
        """
        self.__dict__.update(state)
        self.__modified = False

    def __getstate__(self):
        """Returns state for current packet

        Returns:
            dict: current state of a packet
        """        
        state = self.__dict__.copy()
        return state

    @abstractmethod
    def _parse_raw(self, raw_data, strict=True):
        """rtype: dict"""
        pass

    @classmethod
    def load(cls: Type[T], raw_data, strict=True) -> T:
        """Load packet from iterable (dict, list, etc...)

        Args:
            raw_data (dict | list | iterable): data to load to packet fields
            strict (bool, optional): whether to raise on required fields missing. Defaults to True.

        Returns:
            T: loaded packet
        """
        pckt = cls(__strict=strict, **cls._parse_raw(raw_data, strict))
        pckt.on_packet_loaded()
        return pckt

    def update(self, raw_data):
        """Updates all fields in already existing packet from iterable (dict, list, etc...) 

        Args:
            raw_data (dict | list | iterable): data to update fields to.
        """
        parsed = self._parse_raw(raw_data, strict=True)
        for field_name in self.__fields__.keys():
            if field_name in parsed.keys():
                setattr(self, field_name, parsed[field_name])
        self.on_packet_loaded()

    @classmethod
    def loadz(cls: Type[T], s) -> T:
        """Load packet from zip packed source string

        Returns:
            PacketBase[T]: loaded packet
        """        
        return cls.load(json.loads(s.decode('zip')))

    @classmethod
    def loads(cls: Type[T], s, strict=True) -> T:
        return cls.load(json.loads(s), strict)

    def on_packet_loaded(self):
        """Callback on packet load or update.
        Need to be implemented in children if needed.
        """        
        pass

    @abstractmethod
    def dump(self):
        """Required interface method for packet serialization
        """        
        pass

    def dumpz(self) -> str:
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

    def is_modified(self):
        #type: () -> bool
        modified = self.__modified
        for k in self.__fields__:
            attr = getattr(self, k)
            if isinstance(attr, PacketBase):
                modified = modified or attr.is_modified()
        return modified
    
    def __eq__(self, other):
        if isinstance(other, PacketBase):
            if self.__class__ != other.__class__:
                return False
            if self.__fields__.keys() != other.__fields__.keys():
                return False
            for py_name in self.__fields__.keys():
                if getattr(self, py_name) != getattr(other, py_name):
                    return False
            return True
        return False

    def __ne__(self, other):
        return not self == other

    def __setattr__(self, key, value):
        if key in self.__fields__:
            self.__modified = True
        return super().__setattr__(key, value)

    def __delattr__(self, attr):
        if attr in self.__fields__:
            setattr(self, attr, None)
        else:
            super().__delattr__(attr)

    def __getsetitem(self, path: List[str]) -> Any:
        current = self
        for path_element in path:
            if isinstance(current, PacketBase):
                current = getattr(current, current.__raw_mapping__[path_element])
            elif isinstance(current, (list, tuple)):
                current = current[int(path_element)]
            elif isinstance(current, dict):
                if path_element in current:
                    current = current[path_element]
                else:
                    try:
                        key = int(path_element)
                    except ValueError:
                        current = None
                    else:
                        current = current.get(key, {})  # pylint: disable=no-member
            else:
                raise RuntimeError(f'Unsupported type {current} ({type(current)})')
            if current is None:
                break
        return current

    def __getitem__(self, key: str) -> Any:
        path = key.split('.')
        return self.__getsetitem(path)

    def __setitem__(self, key, value):
        path = key.split('.')

        current = self
        for path_element in path[:-1]:
            if isinstance(current, PacketBase):
                current = getattr(current, path_element)
            elif isinstance(current, (list, tuple)):
                current = current[int(path_element)]
            elif isinstance(current, dict):
                if path_element in current:
                    current = current[path_element]
                else:
                    try:
                        key = int(path_element)
                    except ValueError:
                        current = current.setdefault(path_element, {})  # pylint: disable=no-member
                    else:
                        current = current.setdefault(key, {})  # pylint: disable=no-member
            else:
                raise RuntimeError(f'Unsupported type {current} ({type(current)})')

        tail = path[-1]
        if isinstance(current, PacketBase):
            setattr(current, current.__raw_mapping__[tail], value)
        elif isinstance(current, (list, tuple)):
            current[int(tail)] = value
        else:
            if tail in current:
                current[tail] = value
            else:
                try:
                    key = int(tail)
                except ValueError:
                    current[tail] = value
                else:
                    current[key] = value

    def __delitem__(self, key):
        path = key.split('.')
        current = self.__getsetitem(path[:-1])

        tail = path[-1]
        if isinstance(current, PacketBase):
            if tail in current.__raw_mapping__:
                delattr(current, current.__raw_mapping__[tail])
        elif isinstance(current, list):
            pos = int(tail)
            if len(current) > pos:
                del current[int(tail)]
        else:
            if tail in current:
                del current[tail]
            else:
                try:
                    key = int(tail)
                except ValueError:
                    pass
                else:
                    if key in current:
                        del current[key]

    def __deepcopy__(self, memo):  # pylint: disable=method-hidden
        if 'dont_cpickle' in self.__tags__:
            self.__deepcopy__ = None
            newone = deepcopy(self, memo)
            self.__deepcopy__ = PacketBase.__deepcopy__
            return newone
        else:
            return pickle.loads(pickle.dumps(self, protocol=-1))

    def clone(self):
        return self.__deepcopy__(None)
