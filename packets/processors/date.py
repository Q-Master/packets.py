# -*- coding:utf-8 -*-
import time
import datetime
from numbers import Integral
from ._types import StringTypes, StringTypesTyping, unixtime
from .._fieldprocessorbase import FieldProcessor


__all__ = [
    'DateAsString', 'UnixtimeAsString', 'TimeAsString', 'DateTime', 'UnixTime', 
    'unixtime_t', 'str_datetime_z_t', 'str_datetime_t', 'str_date_t', 'str_time_t', 'str_unixtime_t', 'datetime_t'
]


class DateAsString(FieldProcessor):
    """DateTime processor. Stores `datetime.datetime` as string using `self.format_string`"""
    has_mutable_value = False

    def __init__(self, format_string: str):
        """Constructor

        Args:
            format_string (str): the format string to store and decode datetime value.
        """  
        self.format_string = format_string

    def check_py(self, value: datetime.datetime):
        assert isinstance(value, datetime.datetime), (value, type(value))

    def check_raw(self, value: StringTypesTyping):
        assert isinstance(value, StringTypes), (value, type(value))

    def raw_to_py(self, raw_value: StringTypesTyping, strict: bool) -> datetime.datetime:
        return datetime.datetime.strptime(
            raw_value if isinstance(raw_value, str) else raw_value.decode('utf8'), 
            self.format_string
        )

    def py_to_raw(self, py_value: datetime.datetime) -> str:
        return py_value.strftime(self.format_string)

    @property
    def my_type(self):
        return datetime.datetime


class UnixtimeAsString(FieldProcessor):
    """Unixtime processor. Stores `unixtime` as string using `self.format_string`"""

    def __init__(self, format_string):
        """Constructor

        Args:
            format_string (str): the format string to store and decode datetime value. Timezones are not supported.
        """
        if '%z' in format_string:
            raise NotImplementedError('Timezone dates are not supported')
        self.format_string = format_string

    def check_py(self, value: Integral):
        assert isinstance(value, Integral), (value, type(value))

    def check_raw(self, value: StringTypesTyping):
        assert isinstance(value, StringTypes), (value, type(value))

    def raw_to_py(self, raw_value: StringTypesTyping, strict: bool) -> unixtime:
        return unixtime(time.mktime(datetime.datetime.strptime(
            raw_value if isinstance(raw_value, str) else raw_value.decode('utf8'), 
            self.format_string).timetuple())
        )

    def py_to_raw(self, py_value: Integral) -> str:
        return datetime.datetime.fromtimestamp(float(py_value)).strftime(self.format_string)

    @property
    def my_type(self):
        return unixtime


class TimeAsString(FieldProcessor):
    """Time processor. Stores `datetime.time` as string using `self.format_string`"""
    has_mutable_value = False

    def __init__(self, format_string):
        """Constructor

        Args:
            format_string (str): the format string to store and decode datetime value. Timezones are not supported.
        """
        if '%z' in format_string:
            raise NotImplementedError('Timezone dates are not supported')
        self.format_string = format_string

    def check_py(self, value: datetime.time):
        assert isinstance(value, datetime.time), (value, type(value))

    def check_raw(self, value: StringTypesTyping):
        assert isinstance(value, StringTypes), (value, type(value))

    def raw_to_py(self, raw_value: StringTypesTyping, strict: bool) -> datetime.time:
        return datetime.datetime.strptime(
            raw_value if isinstance(raw_value, str) else raw_value.decode('utf8'), 
            self.format_string
        ).time()

    def py_to_raw(self, py_value) -> str:
        return py_value.strftime(self.format_string)

    @property
    def my_type(self):
        return datetime.time


class DateTime(FieldProcessor):
    """DateTime processor."""

    def check_py(self, py_value):
        assert isinstance(py_value, datetime.datetime), (py_value, type(py_value))

    def check_raw(self, raw_value):
        assert isinstance(raw_value, datetime.datetime), (raw_value, type(raw_value))

    def raw_to_py(self, raw_value, strict) -> datetime.datetime:
        return raw_value

    def py_to_raw(self, value) -> datetime.datetime:
        return value

    @property
    def my_type(self):
        return datetime.datetime


class UnixTime(FieldProcessor):
    """Unixtime processor. Stores `unixtime` as int"""

    def check_py(self, value: unixtime):
        assert isinstance(value, (unixtime, int)), (value, type(value))
        if value < 0:
            raise ValueError(f'{value} < 0. Unixtime cant be negative.')
        if value > 4294967295:
            raise ValueError(f'{value} > 4294967295. Unixtime cant be bigger than 2^32')

    def check_raw(self, value: Integral):
        if value < 0:
            raise ValueError(f'{value} < 0. Unixtime cant be negative.')
        if int(value) > 4294967295:
            raise ValueError(f'{value} > 4294967295. Unixtime cant be bigger than 2^32')

    def raw_to_py(self, raw_value: Integral, strict: bool) -> unixtime:
        return unixtime(raw_value)

    def py_to_raw(self, value: unixtime) -> int:
        return int(value)
    
    @property
    def my_type(self):
        return unixtime


class Time(FieldProcessor):
    """Time processor."""

    def check_py(self, py_value):
        assert isinstance(py_value, datetime.time), (py_value, type(py_value))

    def check_raw(self, raw_value):
        assert isinstance(raw_value, datetime.time), (raw_value, type(raw_value))

    def raw_to_py(self, raw_value, strict) -> datetime.time:
        return raw_value

    def py_to_raw(self, value) -> datetime.time:
        return value

    @property
    def my_type(self):
        return datetime.time


unixtime_t = UnixTime()
str_datetime_z_t = DateAsString(format_string='%Y-%m-%d %H:%M:%S %z')
str_datetime_t = DateAsString(format_string='%Y-%m-%d %H:%M:%S')
str_date_t = DateAsString(format_string='%Y-%m-%d')
str_time_t = TimeAsString(format_string='%H:%M')
str_unixtime_t = UnixtimeAsString(format_string='%Y-%m-%d %H:%M:%S')
datetime_t = DateTime()
