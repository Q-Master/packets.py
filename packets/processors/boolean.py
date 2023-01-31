# coding=utf-8
from numbers import Integral
from ._types import BooleanRawTyping
from ._base import FieldProcessor


__all__ = ['Boolean', 'bool_t']


class Boolean(FieldProcessor):
    """Processor for boolean types"""

    def check_py(self, value: bool):
        assert isinstance(value, bool), (value, type(value))

    def check_raw(self, value: BooleanRawTyping):
        assert isinstance(value, (str, Integral)), (value, type(value))

    def raw_to_py(self, raw_value: BooleanRawTyping, strict: bool) -> bool:
        if isinstance(raw_value, str):
            tmp = raw_value.lower().strip()
            if tmp.isdigit():
                processed_value = bool(float(tmp))
            elif tmp in ('true', 't'):
                processed_value = True
            elif tmp in ('false', 'f'):
                processed_value = False
            else:
                processed_value = bool(tmp)
        else:
            processed_value = bool(raw_value)
        return processed_value

    def py_to_raw(self, py_value: bool) -> str:
        return 'true' if py_value else 'false'

bool_t = Boolean()
