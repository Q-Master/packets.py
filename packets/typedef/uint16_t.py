# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number, NumberAsString


Uint16T: TypeAlias = int
uint16_t = Number[int](int, 0, 65535)
uint16_ts = NumberAsString[int](int, 0, 65535)
