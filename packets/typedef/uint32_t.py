# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number, NumberAsString


Uint32T: TypeAlias = int
uint32_t = Number[int](int, 0, 4294967295)
uint32_ts = NumberAsString[int](int, 0, 4294967295)
