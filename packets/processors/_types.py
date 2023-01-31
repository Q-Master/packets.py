# -*- coding:utf-8 -*-
from typing import Union, Type
import datetime
from ._base import FieldProcessor
from .._packetbase import PacketBase

NumberTyping = Union[int, float]
StringTypes = (str, bytes)
StringTypesTyping = Union[str, bytes]
BooleanType = bool
BooleanRawTyping = Union[str, int]
NoneType = type(None)

class unixtime(int):
    def __str__(self):
        return f"{datetime.datetime.fromtimestamp(self).strftime('%Y-%m-%d %H:%M:%S')}"

SubElementTyping = Union[FieldProcessor, Type[PacketBase]]
