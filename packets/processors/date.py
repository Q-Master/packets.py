# -*- coding:utf-8 -*-
from typing import Type, TypeVar, cast, Self
import datetime
from .base import TypeDef


__all__ = ['DateTime', 'Time']


_DT = TypeVar('_DT', bound=datetime.datetime)


class DateTime(TypeDef[_DT]):
    """DateTime processor. Stores `datetime.datetime` as string using `self._date_format`"""

    def __init__(self, date_format: str):
        """Constructor

        Args:
            date_format (str): the format string to store and decode datetime value.
        """  
        super().__init__()
        self._date_format = date_format

    def check_py(self, v: datetime.datetime) -> bool:
        return isinstance(v, datetime.datetime)
    
    def check_raw(self, r: str) -> bool:
        return isinstance(r, str)
    
    def raw_to_py(self, r: str, strict=True) -> _DT:
        return cast(_DT, datetime.datetime.strptime(r, self._date_format))

    def py_to_raw(self, v: _DT) -> str:
        return v.strftime(self._date_format)

    def zero_value(self) -> _DT:
        return cast(_DT, datetime.datetime.today())

    def self_type(self) -> Type[datetime.datetime]:
        return datetime.datetime
    
    def clone(self) -> Self:
        c = self.__class__(self._date_format)
        c.set_ro(False)
        return c



_T = TypeVar('_T', bound=datetime.time)


class Time(TypeDef[_T]):
    """Time processor. Stores `datetime.time` as string using `self._time_format`"""

    def __init__(self, time_format: str):
        """Constructor

        Args:
            time_format (str): the format string to store and decode datetime value. Timezones are not supported.
        """
        super().__init__()
        if '%z' in time_format:
            raise NotImplementedError('Timezone dates are not supported')
        self._time_format = time_format

    def check_py(self, v: _T) -> bool:
        return isinstance(v, datetime.time)

    def check_raw(self, r: str):
        return isinstance(r, str)

    def raw_to_py(self, r: str, strict: bool) -> _T:
        return cast(_T, datetime.datetime.strptime(r, self._time_format).time())

    def py_to_raw(self, v: _T) -> str:
        return v.strftime(self._time_format)

    def zero_value(self) -> _T:
        return cast(_T, datetime.datetime.today())

    def self_type(self) -> Type[datetime.time]:
        return datetime.time

    def clone(self) -> Self:
        c = self.__class__(self._time_format)
        c.set_ro(False)
        return c
