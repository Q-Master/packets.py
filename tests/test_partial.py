from typing import Optional, List
import unittest
from copy import deepcopy
from packets import Packet, makeField
from packets.processors import int_t, string_t, float_t, Array


class Internal(Packet):
    d: Optional[int] = makeField(int_t)
    e: str = makeField(string_t, required=True)
    f: List[str] = makeField(Array(string_t), default=[])


class Front(Packet):
    a: int = makeField(int_t, default=10)
    b: Optional[float] = makeField(float_t, 'non_B')
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
        pkt.b = 3.0
        pkt.c.e = 'test2'
        pkt.c.d = 8
        pkt.c.f = ['1', '2', '6']
        if pkt.is_modified():
            partial_pkt = pkt.dump_partial({'b': '1', 'c': {'d': '1', 'e': '1', 'f': '1'}})
            self.assertDictEqual(partial_pkt, {'c': {'d': 8, 'e': 'test2', 'f': ['1', '2', '6']}, 'non_B': 3.0})
