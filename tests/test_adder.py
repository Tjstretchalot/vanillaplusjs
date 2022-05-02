"""Very sophisticated test which just imports everything.
"""
import unittest
import helper  # noqa
from adder import add


class Test(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(1, -2), -1)
        self.assertEqual(add(-1, 2), 1)
        self.assertEqual(add(-1, -2), -3)


if __name__ == "__main__":
    unittest.main()
