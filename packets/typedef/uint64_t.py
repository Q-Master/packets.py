# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number, NumberAsString


Uint64T: TypeAlias = int
uint64_t = Number[int](int, 0, 18446744073709551615)
uint64_ts = NumberAsString[int](int, 0, 18446744073709551615)
