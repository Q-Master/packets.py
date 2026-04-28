from typing import Optional, List
import unittest
import pickle
from packets import Packet, makeField
from packets.typedef.int_t import int_t
from packets.typedef.string_t import string_t
from packets.typedef.float_t import float_t
from packets.processors import Array


class Internal(Packet):
    d: Optional[int] = makeField(int_t)
    e: str = makeField(string_t, '_e', required=True)
    f: List[str] = makeField(Array(string_t), default=[])


class Front(Packet):
    a: int = makeField(int_t, default=10)
    b: Optional[float] = makeField(float_t, 'non_B')
    c: Internal = makeField(Internal, required=True)


class InternalPartial(Internal.with_fields('d', 'f')):
    pass

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
            partial_pkt = pkt.dump_partial({'non_B': '1', 'c': {'d': '1', '_e': '1', 'f': '1'}})
            self.assertDictEqual(partial_pkt, {'c': {'d': 8, '_e': 'test2', 'f': ['1', '2', '6']}, 'non_B': 3.0})
class FrontPartial(Front.with_fields(
    'a', 'non_B'
)):
    pass

class TestWithFields(unittest.TestCase):
    def test_with_fields(self):
        with self.assertRaises(TypeError):
            class InternalPartialFail(Internal.with_fields('x', 'f')):
                pass
        self.assertNotIn('e', InternalPartial.field_names())

        pickle.dumps(FrontPartial, -1)
