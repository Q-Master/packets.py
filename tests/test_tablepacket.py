import unittest
import pickle
from multiprocessing import Process
from time import sleep
from packets import ArrayPacket, TablePacket, makeDefaultField, makeField
from packets.typedef.string_t import string_t
from packets.typedef.int_t import int_t
from .process_worker_base import Worker

from wrapt import BaseObjectProxy

tdata = '''
{
    "a": ["check"],
    "b": ["check1"]
}
'''

tdata2 = '''
{
    "a": "check",
    "b": "check1",
    "additional": 3
}
'''


class TableData(ArrayPacket):
    a = makeField(string_t, required=True)


class TestTablePacket(TablePacket[TableData]):
    __default_field__ = makeDefaultField(TableData)
    f: int

    def on_packet_loaded(self):
        self.f = 9


class TestTablePacket2(TablePacket[str]):
    __default_field__ = makeDefaultField(string_t)
    additional = makeField(int_t, default=3)


class TestTablePacketWorker(Worker):
    def __init__(self):
        self.ltp = TestTablePacket.loads(tdata)

    def work(self):
        if self.ltp.a.a != 'check' and self.ltp.f == 9:
            print(f'FAIL')
            raise RuntimeError('FAIL')

class TestTP(unittest.TestCase):
    def test_pickling(self):
        worker = TestTablePacketWorker()
        process = Process(
            target=worker,
            name='{0}W'.format(worker.__class__.__name__)
        )
        process.start()
        while process.is_alive():
            sleep(0.1)
        ltp = TestTablePacket.loads(tdata)
        self.assertEqual(ltp.a.a, 'check')
        self.assertEqual(ltp.b.a, 'check1')
        self.assertEqual(ltp.f, 9)
        pltp = pickle.loads(pickle.dumps(ltp))
        self.assertEqual(pltp.a.a, 'check')
        self.assertEqual(pltp.b.a, 'check1')
        self.assertEqual(pltp.f, 9)
        ltp.a.a = 'check2'
        self.assertEqual(ltp.a.a, 'check2')
        self.assertEqual(ltp.diff_keys(), {'a': {'a': '1'}})
    
    def test_simple(self):
        ltp = TestTablePacket2.loads(tdata2)
        self.assertEqual(ltp.a, 'check')
        self.assertEqual(ltp.b, 'check1')
        self.assertEqual(ltp.additional, 3)
        ltp.b = 'check2'
        ltp.additional = 8
        self.assertEqual(ltp.b, 'check2')
        self.assertEqual(ltp.additional, 8)
        self.assertEqual(ltp.diff_keys(), {'additional': '1', 'b': '1'})
