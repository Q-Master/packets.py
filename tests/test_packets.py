# -*- coding: utf8 -*-
import unittest
from packets import Packet, PacketWithID, ArrayPacket, Field, TablePacket
from packets import string_t, int_t, Array


class schema_case(unittest.TestCase):
    def test_1_1_basic(self):
        DICT = {
            'testStr': 'tested ok',
            'testInt': 17
        }


        class TestSchema(Packet):
            packet_fields = ('testStr', 'testInt')
            #
            testStr = Field(string_t)
            testInt = Field(int_t)


        #
        obj = TestSchema()
        self.assertEquals(obj.dump(), {})
        #
        obj2 = TestSchema.load(DICT)
        self.assertEquals(obj2.dump(), DICT)
        #
        obj3 = TestSchema(**DICT)
        self.assertEquals(obj3.dump(), DICT)
        #
        obj3.testInt = None
        self.assertDictEqual({'testStr': 'tested ok'}, obj3.dump())

    def test_1_2_basic_with_name(self):
        KWARGS = {
            'testStr': 'tested ok',
            'testInt': 17
        }
        DICT = {
            'testStrName': 'tested ok',
            'testIntName': 17
        }


        class TestSchema(Packet):
            testStr = Field(string_t, 'testStrName')
            testInt = Field(int_t, 'testIntName')


        #
        obj = TestSchema()
        self.assertIs(obj.testStr, None)
        #
        obj2 = obj.load(DICT)
        self.assertEquals(obj2.dump(), DICT)
        #
        obj3 = TestSchema(**KWARGS)
        self.assertEquals(obj3.dump(), DICT)

    def test_1_3_merge(self):
        DICT1 = {
            'testStr': 'tested ok',
            'testInt': 255
        }
        DICT2 = {
            'testInt': 17
        }
        DICTR = DICT1
        DICTR.update(DICT2)


        class TestSchema(Packet):
            testStr = Field(string_t)
            testInt = Field(int_t)


        #
        obj = TestSchema(**DICT1)
        obj.update(DICT2)
        self.assertEquals(obj.dump(), DICTR)

    def test_1_4_array(self):
        class TestSchema(ArrayPacket):
            f1 = Field(int_t)
            f2 = Field(string_t)


        packet = TestSchema.load([1, 'pew'])
        self.assertEqual(packet.f1, 1)
        self.assertEqual(packet.f2, 'pew')
        self.assertEqual(packet.dump(), [1, 'pew'])


    def test_2_1_required(self):
        class TestSchema(Packet):
            testStr = Field(string_t, 'TestStrName', required=True)


        #
        self.assertRaises(ValueError, lambda: TestSchema())
        TestSchema(testStr='tested ok')

    def test_2_2_defval(self):
        class TestSchema(Packet):
            testStr = Field(string_t, default='default tested ok')


        #
        obj = TestSchema(testStr='tested ok')
        self.assertEquals(obj.testStr, 'tested ok')
        #
        obj2 = TestSchema()
        self.assertEquals(obj2.testStr, 'default tested ok')

    def test_2_3_default_values_copy(self):
        class TestSchema(Packet):
            arr = Field(Array(string_t), default=['pew'])


        p1 = TestSchema()
        p2 = TestSchema()

        self.assertEqual(p1.arr, ['pew'])
        self.assertEqual(p2.arr, ['pew'])
        self.assertIsNot(p1.arr, p2.arr)

    def test_4_1_snapshot_deepcopy(self):
        global TestPacket
        class TestPacket(Packet):
            f1 = Field(int_t)
            f2 = Field(string_t)
            f3 = Field(Array(int_t))


        p = TestPacket(f1=11, f2='xxx', f3=[22, 33])
        snapshot = p.clone()

        p.f3.append(12)
        p.f2 = 'yyy'
        p.f1 = 2

        self.assertEqual(snapshot.f1, 11)
        self.assertEqual(snapshot.f2, 'xxx')
        self.assertEqual(snapshot.f3, [22, 33])

    def test_update(self):
        class TestPacket(Packet):
            f1 = Field(int_t, 'z1')
            f2 = Field(int_t, 'z2')


        packet = TestPacket(f1=1, f2=2)
        self.assertEqual(packet.f1, 1)
        packet.f1 = 10
        packet.update({'z2': 20})
        self.assertEqual(packet.f1, 10)
        self.assertEqual(packet.f2, 20)

    def test_subclassing(self):
        class Base(Packet):
            pass


        class Some(Base):
            pass


        class Dup(Base):
            pass


        D1 = Dup


        class Dup(Base):
            pass


        D2 = Dup


        class Dup(object):
            pass


        D3 = Dup


        class Child(D1):
            pass


        class OtherChild(Some):
            pass


        class OldStyle():
            pass


        d1 = D1()
        d2 = D2()
        d3 = D3()
        child = Child()
        other_child = OtherChild()

        self.assertIsInstance(d1, D1)
        self.assertIsInstance(d1, D2)
        self.assertIsInstance(d1, Base)

        self.assertIsInstance(d2, D1)
        self.assertIsInstance(d2, D2)
        self.assertIsInstance(d2, Base)

        self.assertNotIsInstance(d3, D2)
        self.assertNotIsInstance(d3, D1)

        self.assertIsInstance(child, D1)
        self.assertIsInstance(child, D2)
        self.assertIsInstance(child, Child)
        self.assertIsInstance(child, Base)

        self.assertIsInstance(other_child, OtherChild)
        self.assertIsInstance(other_child, Base)
        self.assertNotIsInstance(other_child, D1)
        self.assertNotIsInstance(other_child, D2)

        self.assertTrue(issubclass(D1, D2))
        self.assertTrue(issubclass(D1, Base))
        self.assertTrue(issubclass(D2, D1))
        self.assertTrue(issubclass(D2, Base))

        self.assertFalse(issubclass(D3, D2))
        self.assertFalse(issubclass(D3, D1))

        self.assertTrue(issubclass(Child, D1))
        self.assertTrue(issubclass(Child, D2))
        self.assertTrue(issubclass(Child, Base))
        self.assertTrue(issubclass(Child, Child))

        self.assertTrue(issubclass(OtherChild, Base))
        self.assertTrue(issubclass(OtherChild, OtherChild))
        self.assertFalse(isinstance(OtherChild, D1))
        self.assertFalse(isinstance(OtherChild, D2))

        self.assertNotIsInstance(Base, OldStyle)
        self.assertNotIsInstance(OldStyle, Base)
        self.assertFalse(issubclass(OldStyle, Base))
        self.assertFalse(issubclass(Base, OldStyle))

    def test_override(self):
        class Parent(Packet):
            f1 = Field(int_t, 'field1', required=True)


        class Child(Parent):
            f1 = Field(default=3, override=True)


        packet = Child()
        self.assertEqual(packet.dump(), {'field1': 3})

    def test_subpacket(self):
        t = {
            'p': {
                'f1': 1
            },
            'f': 2
        }
        class SubPacket(Packet):
            f1 = Field(int_t)
        class ParentPacket(Packet):
            p = Field(SubPacket)
            f = Field(int_t)
        packet = ParentPacket.load(t)
        self.assertIsInstance(packet.p, SubPacket)
        self.assertEquals(packet.p.f1, 1)
        self.assertEquals(packet.f, 2)
    
    def test_tablepacket(self):
        t = {
            'a': {
                'f1': 1, 
                'f2': "1"
            },
            'b': {
                'f1': 2,
                'f2': "2"
            },
            'c': {
                'f1': 3, 
                'f2': "3"
            }
        }

        class TableField(Packet):
            f1 = Field(int_t)
            f2 = Field(string_t)
        
        class Default(TablePacket):
            __default_field__ = Field(TableField)
        
        packet = Default.load(t)
        self.assertEquals(packet.a.f1, 1)
        self.assertEquals(packet.b.f1, 2)
        self.assertEquals(packet.c.f1, 3)



if __name__ == '__main__':
    unittest.main()
