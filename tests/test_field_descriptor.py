# -*- coding: utf8 -*-
import unittest
from typing import cast
from packets.field import makeField, Field
from packets.packet import Packet, TablePacket
from packets.typedef.int32_t import int32_t
from packets.typedef.string_t import string_t


class FieldDescriptor(unittest.TestCase):
    def test_field_descriptor(self):
        class TestPacket1(Packet):
            field_1 = makeField(int32_t)

        class TestPacket2(Packet):
            field_1 = makeField(int32_t, 'f2')
        
        a1 = TestPacket1()
        a2 = TestPacket2()
        a1.field_1 = 9
        a2.field_1 = 10
        self.assertEqual(a1.field_1, 9)
        self.assertEqual(a2.field_1, 10)
        print(cast(Field, TestPacket1.field_1).name)
        self.assertEqual(vars(TestPacket2)['field_1'].name, 'f2')

    def test_field_descriptor_inheritance(self):
        class TestPacket1(Packet):
            field_1 = makeField(int32_t)

        class TestPacket2(TestPacket1):
            field_2 = makeField(string_t)
        
        a = TestPacket2(field_1 = 1, field_2 = '1')
        self.assertEqual(a.field_1, 1)
        self.assertEqual(a.field_2, '1')

    def test_field_descriptor_load_dump(self):
        class TestPacket1(Packet):
            field_1 = makeField(int32_t)

        class TestPacket2(TestPacket1):
            field_2 = makeField(string_t)
        
        a = TestPacket2(field_1 = 1, field_2 = '1')
        a_dump = a.dump()
        print(a_dump)
        b = TestPacket2.load(a_dump)
        self.assertEqual(a, b)

    def test_field_descriptor_with_fields(self):
        class TestPacket1(Packet):
            field_1 = makeField(int32_t)
            field_2 = makeField(int32_t)
            field_3 = makeField(string_t)
            field_4 = makeField(string_t)

        class TestPacket2(TestPacket1.with_fields('field_1', 'field_4')):
            field_5 = makeField(int32_t)
        
        a = TestPacket2(field_1=1, field_4 = '1', field_5=2)


    def test_field_descriptor_table_packet(self):
        js = {'field1': {'f1': 1, 'f2': '1'}, 'field2': {'f1': 2, 'f2': '2'}, 'field3': {'f1': 3, 'f2': '3'}}
        class InternalData(Packet):
            f1 = makeField(int32_t)
            f2 = makeField(string_t)
        class TestPacket1(TablePacket[InternalData]):
            __default_field__ = makeField(InternalData, required=True)
        
        a = TestPacket1.load(js)
        self.assertEqual(a.field1.f1, 1)
        self.assertEqual(a.field1.f2, '1')
        self.assertEqual(a.field2.f1, 2)
        self.assertEqual(a.field2.f2, '2')
        self.assertEqual(a.field3.f1, 3)
        self.assertEqual(a.field3.f2, '3')
