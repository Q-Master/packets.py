# -*- coding: utf8 -*-
from typing import TypeAlias
from ..processors.numeric import NumberAsString


str_int_t = NumberAsString[int](int)
StrIntT: TypeAlias = int
