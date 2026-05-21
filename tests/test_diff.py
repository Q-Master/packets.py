from typing import Optional, List, Dict
import unittest
from packets import Packet, makeField
from packets.processors import Array
from packets.processors import Hash
from packets.typedef.int_t import int_t
from packets.typedef.string_t import string_t
from packets.typedef.float_t import float_t 

class Internal(Packet):
    d: Optional[int] = makeField(int_t)
    e: str = makeField(string_t, '_e', required=True)
    f: List[str] = makeField(Array(string_t), default=[])


class Front(Packet):
    a: int = makeField(int_t, '_a', default=10)
    b: Optional[float] = makeField(float_t)
    c: Internal = makeField(Internal, required=True)


class DPTest(Packet):
    a: int = makeField(int_t, '_a', required=True)
    b: Dict[str, str] = makeField(Hash(string_t, string_t), default={})
    c: List[int] = makeField(Array(int_t), default=[])


class TestPacketDiff(unittest.TestCase):
    def test_packet_diff(self):
        pkt = Front(
            a = 10, b = 4.0,
            c = Internal(
                e = 'test',
                f = ['1', '2', '3', '4']
            )
        )
        pkt.a = 0
        pkt.c.e = 'test2'
        pkt.c.d = 8
        pkt.c.f = ['1', '2', '6']
        if pkt.is_modified():
            keys_diff = pkt.diff_keys()
            self.assertIsInstance(keys_diff, dict)
            self.assertDictEqual(keys_diff, {'_a': '1', 'c': {'_e': '1', 'd': '1', 'f': '1'}})


class TestDumpPartial(unittest.TestCase):
    def test_dump_partial(self):
        pkt = DPTest(a=1, b={'1': '1', '2': '2', '3':'3'}, c=[1,2,3])
        pkt.a = 2
        pkt.b['2'] = 'not 2'
        pkt.c = [1, 2, 4]
        self.assertEqual(pkt.is_modified(), True)
        kd = pkt.diff_keys()
        self.assertDictEqual(pkt.dump_partial(kd), {'_a': 2, 'b': {'2': 'not 2'}, 'c': [1, 2, 4]})

