import unittest

from code_under_test import fully_covered_add, non_fully_covered_add


class TestSuite(unittest.TestCase):
    def test_fully_covered_add(self):
        result = fully_covered_add(2, 3)
        self.assertEqual(result, 5)

    def test_non_fully_covered_add(self):
        result = non_fully_covered_add(2, 3)
        self.assertEqual(result, 5)
