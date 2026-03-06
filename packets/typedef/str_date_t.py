# -*- coding:utf-8 -*-
from typing import TypeAlias
import datetime
from ..processors.date import DateTime


str_date_t = DateTime('%Y-%m-%d')
StrDateT: TypeAlias = datetime.datetime
