# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number


uint16_t = Number[int](int, 0, 65535)
UInt16T: TypeAlias = int
