# -*- coding:utf-8 -*-
from . import _json as json
from ._packetbase import PacketBase
from ._types import DiffKeys
from ._util import field_name
from .packet import Packet, TablePacket, ArrayPacket
from .field import Field, makeField
from .processors.base import TypeDef


__all__ = [
    'json', 
    'PacketBase', 'Packet', 'TablePacket', 'ArrayPacket', 'DiffKeys', 
    'Field', 'makeField', 'TypeDef', 'field_name'
]


__version__ = '0.21.1'

__title__ = 'packets'
__description__ = 'Packets system for serialization/deserialization.'
__url__ = 'https://github.com/Q-Master/packets.py'
__uri__ = __url__
__doc__ = f"{__description__} <{__uri__}>"

__author__ = 'Vladimir Berezenko'
__email__ = 'qmaster2000@gmail.com'

__license__ = 'MIT'
__copyright__ = 'Copyright 2019-2026 Vladimir Berezenko'
