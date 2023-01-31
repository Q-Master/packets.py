# -*- coding:utf-8 -*-
from typing import Type
from numbers import Integral, Real
from ._base import FieldProcessor
from ._types import NumberTyping


__all__ = [
    'Number', 'NumberAsString', 'Percent', 'float_t', 'double_t', 'int8_t', 'uint8_t', 
    'int16_t', 'uint16_t', 'int32_t', 'uint32_t', 'int_t', 'uint_t', 'int64_t' ,'uint64_t', 'long_t', 'str_int_t', 'percent_t'
]


class Number(FieldProcessor):
    """Any number processor"""
    has_mutable_value = False

    valid_types = {
        int: Integral,
        float: Real,
    }

    def __init__(self, number_type: Type[NumberTyping], min_=None, max_=None):
        """Constructor

        Args:
            number_type (int | float): type of number. Might be `int` or `float`.
            min_ (int|float, optional): minimal value for type. Defaults to None.
            max_ (int|float, optional): maximum value for type. Defaults to None.
        """
        self._number_type = number_type
        self.min = min_
        self.max = max_
        self._type_for_checks = self.valid_types[number_type]
        if self.min:
            self.zero_value = number_type(self.min)
        else:
            self.zero_value = number_type(0)

    def check_py(self, value: NumberTyping):
        assert isinstance(value, self._type_for_checks), (value, type(value), self._type_for_checks)
        if self.min is not None and value < self.min:
            raise ValueError(f'{value} < {self.min}')
        if self.max is not None and value > self.max:
            raise ValueError(f'{value} > {self.max}')

    def check_raw(self, value: NumberTyping):
        if self.min is not None and self._number_type(value) < self.min:
            raise ValueError(f'{value} < {self.min}')
        if self.max is not None and self._number_type(value) > self.max:
            raise ValueError(f'{value} > {self.max}')

    def raw_to_py(self, raw_value: NumberTyping, strict: bool):
        processed_value = self._number_type(raw_value)
        return processed_value

    def py_to_raw(self, value: NumberTyping):
        return self._number_type(value)

    def to_number_as_string(self):
        return NumberAsString(self._number_type, self.min, self.max)


class NumberAsString(Number):
    """Same as simple `Number`, but serializes itself to string"""
    def check_py(self, value):
        value = self._number_type(float(value))
        super(NumberAsString, self).check_py(value)

    check_raw = check_py

    def raw_to_py(self, raw_value: str, strict: bool): # type: ignore[override]
        processed_value = self._number_type(float(raw_value))
        return processed_value

    def py_to_raw(self, value) -> str:
        return str(value)


class Percent(Number):
    """Percent number processor"""
    def raw_to_py(self, *args, **kwargs) -> float:
        result = super(Percent, self).raw_to_py(*args, **kwargs)
        if result is not None:
            return result / 100.
        return 0

    def py_to_raw(self, value):
        return super(Percent, self).py_to_raw(value) * 100.


float_t = Number(float)
double_t = float_t
int8_t = Number(int, -128, 127)
uint8_t = Number(int, 0, 255)
int16_t = Number(int, -32768, 32767)
uint16_t = Number(int, 0, 65535)
int32_t = Number(int, -2147483648, 2147483647)
uint32_t = Number(int, 0, 4294967295)
int_t = int32_t
uint_t = uint32_t
int64_t = Number(int, -9223372036854775808, 9223372036854775807)
uint64_t = Number(int, 0, 18446744073709551615)
long_t = int64_t
str_int_t = NumberAsString(int)
percent_t = Percent(float, 0, 100)
