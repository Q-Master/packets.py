from typing import Optional, List
import unittest
from copy import deepcopy
from packets import Packet, makeField
from packets.processors import Array
from packets.typedef.int_t import int_t
from packets.typedef.string_t import string_t
from packets.typedef.float_t import float_t 

class Internal(Packet):
    d: Optional[int] = makeField(int_t)
    e: str = makeField(string_t, required=True)
    f: List[str] = makeField(Array(string_t), default=[])


class Front(Packet):
    a: int = makeField(int_t, default=10)
    b: Optional[float] = makeField(float_t)
    c: Internal = makeField(Internal, required=True)


class TestPacketDiff(unittest.TestCase):
    def test_packet_diff(self):
        pkt = Front(
            a = 10, b = 4.0,
            c = Internal(
                e = 'test',
                f = ['1', '2', '3', '4']
            )
        )
        print('a')
        pkt.a = 0
        print('c.e')
        pkt.c.e = 'test2'
        print('c.d')
        pkt.c.d = 8
        print('c.f')
        pkt.c.f = ['1', '2', '6']
        if pkt.is_modified():
            keys_diff = pkt.diff_keys()
            self.assertIsInstance(keys_diff, dict)
            self.assertDictEqual(keys_diff, {'a': '1', 'c': {'d': '1', 'e': '1', 'f': '1'}})
