# -*- coding:utf-8 -*-
from typing import cast, Any
from .field import Field


__all__ = ['field_name']


def field_name(f: Any) -> str:
    """Just a sugar to get name from a field.

    This code is blindly force any object to `Field` and tries to get it's name,
    so it may fail at any time if f is not `Field` instance.

    Args:
        f (Any): Must be a `Field` instance !

    Returns:
        str: the raw name of a field
    """
    return cast(Field, f).name
