# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number


uint8_t = Number[int](int, 0, 255)
Uint8T: TypeAlias = int
