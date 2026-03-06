# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Number


float_t = Number[float](float)
FloatT: TypeAlias = float
