# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number


uint64_t = Number[int](int, 0, 18446744073709551615)
Uint64T: TypeAlias = int
