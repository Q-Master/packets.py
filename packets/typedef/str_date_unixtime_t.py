# -*- coding:utf-8 -*-
from typing import Type, TypeAlias, Self
import time
import datetime
from ..processors.base import TypeDef
from .unixtime_t import UnixtimeT


StrDateUnixtimeT: TypeAlias = UnixtimeT


class UnixtimeAsDateString(TypeDef[StrDateUnixtimeT]):
    """Unixtime processor. Stores `unixtime` as string using `self._date_format`"""

    def __init__(self, date_format: str):
        """Constructor

        Args:
            date_format (str): the format string to store and decode datetime value.
        """
        super().__init__()

        if '%z' in date_format:
            raise NotImplementedError('Timezone dates are not supported')
        self._date_format = date_format
    
    def check_py(self, v: StrDateUnixtimeT) -> bool:
        if v < 0 or v > 4294967295:
            return False
        return isinstance(v, StrDateUnixtimeT)
    
    def check_raw(self, r: str) -> bool:
        return isinstance(r, str)
    
    def raw_to_py(self, r: str, strict=True) -> StrDateUnixtimeT:
        return StrDateUnixtimeT(time.mktime(
            datetime.datetime.strptime(r, self._date_format).timetuple()
        ))

    def py_to_raw(self, v: StrDateUnixtimeT) -> str:
        return datetime.datetime.fromtimestamp(float(v)).strftime(self._date_format)

    def zero_value(self) -> StrDateUnixtimeT:
        return StrDateUnixtimeT(time.time())

    def self_type(self) -> Type[StrDateUnixtimeT]:
        return StrDateUnixtimeT
    
    def clone(self) -> Self:
        c = self.__class__(self._date_format)
        c.set_ro(False)
        return c


str_date_unixtime_t = UnixtimeAsDateString('%Y-%m-%d %H:%M:%S')
