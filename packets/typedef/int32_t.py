# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number


int32_t = Number[int](int, -2147483648, 2147483647)
Int32T: TypeAlias = int
