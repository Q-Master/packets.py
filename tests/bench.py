# -*- coding: utf8 -*-
import timeit
from packets.field import makeField as makeFieldDesc
from packets.packet import Packet as PacketDesc
from packets.typedef.int32_t import int32_t as int32_tD
from packets.typedef.string_t import string_t as string_tD

class DescriptorPacket(PacketDesc):
    f1 = makeFieldDesc(string_tD)
    f2 = makeFieldDesc(string_tD)
    f3 = makeFieldDesc(int32_tD)


test_data = {'f1': 'Очень длинная строка в для проверки на копирования и прочее, должно быть быстрее в новой версии', 'f2': 'Уже не очень длинная строка', 'f3': 8885855}

time_d = timeit.timeit(stmt='rp = DescriptorPacket.load(test_data)', globals={'DescriptorPacket': DescriptorPacket, 'test_data': test_data})

print(f'Новый пакет {time_d}')

a: int = 7

setattr(a, "__modified__", True)
