# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import Percent


percent_t = Percent(float, 0, 100)
PercentT: TypeAlias = float
