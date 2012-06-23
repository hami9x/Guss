import unittest
from google.appengine.ext import ndb
from guss import model

class DummyModel(model.FormModel):
    a = ndb.StringProperty(verbose_name="AAAA")
    b = ndb.StringProperty()
    c = model.UnsavedProperty(verbose_name="This is a name")

    def _validation(self):
        return [
                ("a", "word"),
                ("b", "word")
                ]

class TestUnsavedProperty(unittest.TestCase):
    def setUp(self):
        self.model = DummyModel()

    def test_verbose_name(self):
        #this method will also make sure that the descriptor methods work
        self.model.c = "a value"
        self.assertEqual(self.model.get_verbose_name("c"), "This is a name")


class TestModel(unittest.TestCase):
    def test_validation(self):
        self.model = DummyModel(a = "****", b = ".....")
        self.assertEqual(self.model.validate(), False)
        self.assertEqual(len(self.model.get_errors()), 2)

        self.model = DummyModel(a = "dkdkf", b = "kdkkdf")
        self.assertEqual(self.model.validate(), True)
        self.assertEqual(self.model.get_errors(), {})

    def test_verbose_name(self):
        self.assertEqual(self.model.get_verbose_name("a"), "AAAA")

