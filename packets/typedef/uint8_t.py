# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number, NumberAsString


Uint8T: TypeAlias = int
uint8_t = Number[int](int, 0, 255)
uint8_ts = NumberAsString[int](int, 0, 255)
