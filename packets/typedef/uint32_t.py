# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number


uint32_t = Number[int](int, 0, 4294967295)
UInt32T: TypeAlias = int
