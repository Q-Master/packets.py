# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number, NumberAsString


FloatT: TypeAlias = float
float_t = Number[float](float)
float_ts = NumberAsString[float](float)
