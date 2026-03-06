# -*- coding:utf-8 -*-
from typing import TypeAlias
import datetime
from ..processors.date import DateTime


str_datetime_z_t = DateTime('%Y-%m-%d %H:%M:%S %z')
StrDatetimeZT: TypeAlias = datetime.datetime
