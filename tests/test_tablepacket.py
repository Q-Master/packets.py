import unittest
import pickle
from multiprocessing import Process
from time import sleep
from packets import ArrayPacket, TablePacket, makeDefaultField, makeField
from packets.typedef.string_t import string_t
from .process_worker_base import Worker


tdata = '''
{
    "a": ["check"],
    "b": ["check1"]
}
'''


class TableData(ArrayPacket):
    a = makeField(string_t, required=True)


class TestTablePacket(TablePacket[TableData]):
    __default_field__ = makeDefaultField(TableData)


class TestTablePacketWorker(Worker):
    def __init__(self):
        self.ltp = TestTablePacket.loads(tdata)

    def work(self):
        if self.ltp.a.a != "check":
            print(f'FAIL')
            raise RuntimeError("FAIL")

class TestTP(unittest.TestCase):
    def test_pickling(self):
        worker = Worker()
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
        pltp = pickle.loads(pickle.dumps(ltp))
        self.assertEqual(pltp.a.a, 'check')
        self.assertEqual(pltp.b.a, 'check1')
        ltp.a.a = 'check2'
        self.assertEqual(ltp.a.a, 'check2')
        self.assertEqual(ltp.diff_keys(), {'a': {'a': '1'}})
