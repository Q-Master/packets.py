from typing import Optional, List, Dict
import unittest
from packets import Packet, makeField, UpdateData
from packets.processors import Array, ArrayT
from packets.processors import Hash, HashT
from packets.typedef.int_t import int_t
from packets.typedef.string_t import string_t
from packets.typedef.float_t import float_t 


class Internal(Packet):
    d: Optional[int] = makeField(int_t)
    e: str = makeField(string_t, '_e', required=True)
    f: List[str] = makeField(Array(string_t), default=[])
    g: Dict[str, str] = makeField(Hash(string_t, string_t), default={})


class Front(Packet):
    a: int = makeField(int_t, '_a', default=10)
    b: Optional[float] = makeField(float_t)
    c: Internal = makeField(Internal, required=True)


class DPTest(Packet):
    a: int = makeField(int_t, '_a', required=True)
    b: Dict[str, str] = makeField(Hash(string_t, string_t), default={})
    b1: Dict[str, int] = makeField(Hash(string_t, int_t), default={})
    c: List[int] = makeField(Array(int_t), default=[])


class FrontPropagate(Packet):
    a: int = makeField(int_t, '_a', default=10)
    b: Optional[float] = makeField(float_t)
    c: Optional[Internal] = makeField(Internal)
    d: HashT[str, str] = makeField(Hash(string_t, string_t), default={})
    e: ArrayT[int] = makeField(Array(int_t), default=[])



class HashPropogateInt(Packet):
    a: int = makeField(int_t, '_a', default=10)
    b: Optional[float] = makeField(float_t)
    c: int = makeField(int_t, required=True)

class HashPropagate(Packet):
    a: int = makeField(int_t, '_a', default=10)
    b: HashT[str, HashPropogateInt] = makeField(Hash(string_t, HashPropogateInt), default={})

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
        self.assertEqual(pkt.is_modified(), True)
        keys_diff = pkt.diff_keys()
        self.assertIsInstance(keys_diff, dict)
        self.assertDictEqual(keys_diff, {'_a': '1', 'c': {'_e': '1', 'd': '1', 'f': '1'}})

    def test_dump_partial(self):
        pkt = DPTest(a=1, b={'1': '1', '2': '2', '3':'3'}, b1={'1': 1, '2': 2, '3': 3}, c=[1,2,3])
        pkt.a = 2
        pkt.b['2'] = 'not 2'
        pkt.b1['3'] = 7
        pkt.c = [1, 2, 4]
        self.assertEqual(pkt.is_modified(), True)
        kd = pkt.diff_keys()
        self.assertDictEqual(pkt.dump_partial(kd), {'_a': 2, 'b': {'2': 'not 2'}, 'b1': {'3': 7}, 'c': [1, 2, 4]})

    def test_update_partial(self):
        pkt = Front(
            a = 10, b = 4.0,
            c = Internal(
                e = 'test',
                f = ['1', '2', '3', '4'],
                g = {'1': '2'}
            )
        )
        self.assertEqual(pkt.dump(), {'_a': 10, 'b': 4.0, 'c': {'_e': 'test', 'f': ['1', '2', '3', '4'], 'g': {'1': '2'}}})

        update = UpdateData({
            '_a': 2,
            'b': None,
            'c': UpdateData({
                '_e': 'done', 
                'f': UpdateData({'0': 7}), 
                'g': UpdateData({'3': '4'})
            })
        })
        pkt.update_partial(update)
        self.assertEqual(pkt.dump(), {'_a': 2, 'c': {'_e': 'done', 'f': ['7', '2', '3', '4'], 'g': {'1': '2', '3': '4'}}})

    def test_propagate_diff(self):
        pkt = FrontPropagate(
            a = 10, b = 4.0, e = [9]
        )
        pkt.c = Internal(
            e = 'test',
            f = ['1', '2', '3', '4'],
            g = {'1': '2'}
        )
        pkt.d['1'] = '2'
        pkt.e.append(10)
        dk = pkt.diff_keys()
        self.assertEqual(dk, {'c': '1', 'd': {'1': '1'}, 'e': '1'})
        self.assertEqual(pkt.dump_partial(dk), {'c': {'_e': 'test', 'f': ['1', '2', '3', '4'], 'g': {'1': '2'}}, 'd': {'1': '2'}, 'e': [9, 10]})

    def test_array_diff(self):
        pkt = FrontPropagate(
            a = 10, b = 4.0, e = [9]
        )
        pkt.c = Internal(
            e = 'test',
            f = ['1', '2', '3', '4'],
            g = {'1': '2'}
        )
        pkt.d['1'] = '2'
        pkt.e[0] = 7
        dk = pkt.diff_keys()
        self.assertEqual(dk, {'c': '1', 'd': {'1': '1'}, 'e': '1'})
        self.assertEqual(pkt.dump_partial(dk), {'c': {'_e': 'test', 'f': ['1', '2', '3', '4'], 'g': {'1': '2'}}, 'd': {'1': '2'}, 'e': [7]})

    def test_hash_propagate(self):
        pkt = HashPropagate(b={'1': HashPropogateInt(c=1)})
        pkt.b['2'] = HashPropogateInt(c=2)
        pkt.b['1'].a = 5
        dk = pkt.diff_keys()
        self.assertEqual(dk, {'b': {'1': {'_a': '1'}, '2': '1'}})
        self.assertEqual(pkt.dump_partial(dk), {'b': {'1': {'_a': 5}, '2': {'_a': 10, 'c': 2}}})
