# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number, NumberAsString


Int32T: TypeAlias = int
int32_t = Number[int](int, -2147483648, 2147483647)
int32_ts = NumberAsString[int](int, -2147483648, 2147483647)
