# -*- coding:utf-8 -*-
from typing import TypeAlias
import datetime
from ..processors.date import Time


str_time_t = Time('%H:%M')
StrTimeT: TypeAlias = datetime.time
