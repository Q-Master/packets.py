# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number, NumberAsString


Int8T: TypeAlias = int
int8_t = Number[int](int, -128, 127)
int8_ts = NumberAsString[int](int, -128, 127)
