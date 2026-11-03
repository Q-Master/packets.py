from packets import Packet, ArrayPacket, Field, TablePacket, makeField, makeDefaultField
from packets.typedef.string_t import string_t
from packets.typedef.int_t import int_t


class TableData(ArrayPacket):
    a = makeField(string_t, required=True)


class TestTablePacket(TablePacket[TableData]):
    __default_field__ = makeDefaultField(TableData)
    my_field: int

    def on_packet_loaded(self):
        self.my_field = 9


tdata = '''
{
    "a": ["check"],
    "b": ["check1"]
}
'''

t = TestTablePacket.loads(tdata)
print(dir(t))
print()
print(dir(t.__class__))
print()
print(t.__dict__)
print()
print(t.__class__.__dict__)