# -*- coding:utf-8 -*-
import logging
from ._base import FieldProcessor
from ._types import StringTypes, StringTypesTyping


__all__ = ['LogLevel', 'log_level_t']


str_to_level = {
    'critical': logging.CRITICAL,
    'fatal': logging.FATAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}

level_to_str = {
    logging.CRITICAL: 'critical',
    logging.FATAL: 'fatal',
    logging.ERROR: 'error',
    logging.WARNING: 'warning',
    logging.WARNING: 'warn',
    logging.INFO: 'info',
    logging.DEBUG: 'debug'
}


class LogLevel(FieldProcessor):
    """Processor for loglevels"""
    has_mutable_value = False
    zero_value = ''

    def check_py(self, value: int):
        assert value in level_to_str.keys()

    def check_raw(self, value: StringTypesTyping):
        assert isinstance(value, StringTypes)
        rval: str
        if isinstance(value, bytes):
            rval = value.decode('utf-8')
        else:
            rval = value
        assert rval.lower() in str_to_level.keys()

    def raw_to_py(self, raw_value: StringTypesTyping, strict: bool) -> int:
        rval: str
        if isinstance(raw_value, bytes):
            rval = raw_value.decode('utf-8')
        else:
            rval = raw_value
        return str_to_level[rval.lower()]

    def py_to_raw(self, py_value: int) -> str:
        return level_to_str[py_value]

log_level_t = LogLevel()
