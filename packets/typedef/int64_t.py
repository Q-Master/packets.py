# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number


int64_t = Number[int](int, -9223372036854775808, 9223372036854775807)
Int64T: TypeAlias = int
