# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number


int16_t = Number[int](int, -32768, 32767)
Int16T: TypeAlias = int
