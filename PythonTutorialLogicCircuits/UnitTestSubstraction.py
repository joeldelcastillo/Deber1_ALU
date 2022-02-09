import unittest
from main import Substraction

class Test8Bits(unittest.TestCase):
L
    def test1(self):
        self.assertEqual(Substraction('11000000', '10101000'), [True, False, False, False, True, True, False, False,
                                                            False])

    def test2(self):
        self.assertEqual(Substraction('11000010', '00101010'), [True, True, False, False, True, True, False, False,
                                                            False])

    def test3(self):
        self.assertEqual(Substraction('11001001', '11011100'), [True, True, True, False, True, True, False, True])



if __name__ == '__main__':

    unittest.main()