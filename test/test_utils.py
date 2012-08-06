import unittest
from guss import utils

class TestUtils(unittest.TestCase):
    def test_slugify(self):
        self.assertEqual(utils.slugify(u"abc đè"), "abc-de")
        self.assertEqual(utils.slugify("^^^"), "untitled")
