# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number


int8_t = Number[int](int, -128, 127)
Int8T: TypeAlias = int
