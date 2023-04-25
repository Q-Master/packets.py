# -*- coding:utf-8 -*-
from . import _json as json
from .packet import *
from ._packetbase import *
from .field import *
from .processors import *

__version__ = '0.7.0'

__title__ = 'packets'
__description__ = 'Packets system for serialization/deserialization.'
__url__ = 'https://github.com/Q-Master/packets.py'
__uri__ = __url__
__doc__ = f"{__description__} <{__uri__}>"

__author__ = 'Vladimir Berezenko'
__email__ = 'qmaster2000@gmail.com'

__license__ = 'MIT'
__copyright__ = 'Copyright 2019-2023 Vladimir Berezenko'
