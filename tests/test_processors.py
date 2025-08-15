# -*- coding:utf-8 -*-
import unittest
import enum
from packets.field import Field
from packets.packet import Packet
from packets.processors.bitmask import BitMask
from packets.processors import *


class Colors(enum.Enum):
    red = 1
    green = 2
    blue = 3


class Sub(Packet):
    f1 = Field(int_t)


class Caps(enum.Enum):
    a = 0
    b = 1
    c = 2
    d = 3
    e = 4
    z = 31


class ProcessorsTestCase(unittest.TestCase):
    def test_numeric(self):
        processor = Number(int, 0, 8)
        self.assertRaises(AssertionError, processor.check_py, 0.0)
        self.assertRaises(ValueError, processor.check_py, -1)
        self.assertRaises(ValueError, processor.check_py, 9)
        self.assertIsInstance(processor.py_to_raw(5), int)

    def test_hash(self):
        processor = Hash(int_t, string_t)
        self.assertEqual({1: '2', 3: '4'}, processor.raw_to_py({'1.0': '2', '3': '4'}, True))
        self.assertEqual({'1': '2', '3': '4'}, processor.py_to_raw({'1': '2', '3': '4'}))
        processor.my_type

    def test_array(self):
        processor = Array(int_t, 3)
        self.assertEqual([1, 2, 3], processor.raw_to_py([1, 2, 3], True))

    def test_enum(self):
        processor = Enumeration(Colors)
        self.assertIs(processor.raw_to_py(2, True), Colors.green)
        self.assertEqual(processor.py_to_raw(Colors.red), 1)

    def test_string(self):
        processor = String(max_length=5, trim=True)
        self.assertEqual(processor.raw_to_py('123456', True), '12345')
        self.assertEqual(processor.py_to_raw('654321'), '65432')

    def test_subpacket(self):
        processor = SubPacket(Sub)
        self.assertEqual(processor.py_to_raw(Sub(f1=3)), {'f1': 3})
        self.assertEqual(processor.raw_to_py({'f1': 4}, True).f1, 4)

    def test_bitmask(self):
        processor = BitMask(Caps)
        self.assertEqual(processor.py_to_raw({Caps.a, Caps.b, Caps.e}), 2 ** 0 + 2 ** 1 + 2 ** 4)
        self.assertEqual(processor.raw_to_py(17, True), {Caps.a, Caps.e})
        self.assertEqual(processor.raw_to_py(17 + 256, True), {Caps.a, Caps.e})
        self.assertEqual(processor.raw_to_py(2 ** 4 + 2 ** 31, True), {Caps.z, Caps.e})
