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

    def test_call(self) -> bool:
            return True


class InternalPartial(Internal.with_fields('d', 'f')):
    pass


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

    def test_pickling(self):
        fp_pickled_class = pickle.loads(pickle.dumps(FrontPartial, -1))
        self.assertNotHasAttr(fp_pickled_class, 'test_call')
        fp = Front(c = Internal(e='1'))
        self.assertHasAttr(fp, 'test_call')
        self.assertEqual(True, fp.test_call())
        fp_pickled = pickle.loads(pickle.dumps(fp, -1))
        self.assertHasAttr(fp_pickled, 'test_call')
        fp_pickled_pickled = pickle.loads(pickle.dumps(fp_pickled, -1))
        self.assertHasAttr(fp_pickled_pickled, 'test_call')
        self.assertEqual(fp_pickled_pickled.test_call(), True)
