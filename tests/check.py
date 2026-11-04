import pickle
from multiprocessing import Process
from time import sleep
from packets import ArrayPacket, TablePacket, makeDefaultField, makeField
from packets.typedef.string_t import string_t
from packets.typedef.int_t import int_t
from process_worker_base import Worker


class TableData(ArrayPacket):
    a = makeField(string_t, required=True)


class TestTablePacket(TablePacket[TableData]):
    __default_field__ = makeDefaultField(TableData)
    _my_field = {}

    def on_packet_loaded(self):
        self._my_field = {0: 1, 1: 2, 2: 3}

class TestTablePacketWorker(Worker):
    def __init__(self):
        self.t = TestTablePacket.loads(tdata)

    def work(self):
        print('SUBPROCESS')
        print(f'DICT: {self.t.__dict__}')
        print()
        print(f'CLS DICT: {self.t.__class__.__dict__}')

tdata = '''
{
    "a": ["check"],
    "b": ["check1"]
}
'''

if __name__ == '__main__':
    print(TestTablePacket.__dict__)
    t = TestTablePacket.loads(tdata)
    t.set_ro(True)
    print('NORMAL')
    print(f'DICT: {t.__dict__}')
    print()
    print(f'CLS DICT: {t.__class__.__dict__}')

    pt = pickle.loads(pickle.dumps(t))
    print('PICKLED')
    print(f'DICT: {pt.__dict__}')
    print()
    print(f'CLS DICT: {pt.__class__.__dict__}')

    worker = TestTablePacketWorker()
    process = Process(
        target=worker,
        name='{0}W'.format(worker.__class__.__name__)
    )
    process.start()
    while process.is_alive():
        sleep(0.1)
