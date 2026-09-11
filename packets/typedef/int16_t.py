# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number, NumberAsString


Int16T: TypeAlias = int
int16_t = Number[int](int, -32768, 32767)
int16_ts = NumberAsString[int](int, -32768, 32767)
