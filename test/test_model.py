import unittest
from google.appengine.ext import ndb
from guss import model

class DummyModel(model.FormModel):
    a = ndb.StringProperty(verbose_name="AAAA")
    b = ndb.StringProperty()
    c = model.UnsavedProperty(verbose_name="This is a name")
    d = ndb.StringProperty(repeated=True)

    def _validation(self):
        return {
                "a": {"required": (), "word": ()},
                "b": {"word": ()},
                }

class TestUnsavedProperty(unittest.TestCase):
    def setUp(self):
        self.model = DummyModel()

    def test_verbose_name(self):
        #this method will also make sure that the descriptor methods work
        self.model.c = "a value"
        self.assertEqual(self.model.get_verbose_name("c"), "This is a name")

class TestModel(unittest.TestCase):
    def setUp(self):
        self.model = DummyModel(a="****", b=".....")
        self.model2 = DummyModel(a="dkdkf", b="kdkkdf")
    def test_validation(self):
        self.assertEqual(self.model.validate(), False)
        self.assertEqual(len(self.model.get_errors()), 2)

        self.assertEqual(self.model2.validate(), True)
        self.assertEqual(self.model2.get_errors(), {})

    def test_verbose_name(self):
        self.model = DummyModel(a="****", b=".....")
        self.assertEqual(self.model.get_verbose_name("a"), "AAAA")

    def test_assign(self):
        class DummyRequestHandler:
            class Request:
                class Post:
                    def dict_of_lists(self):
                        return {
                                "a": ["aaa"],
                                "d": ["b", "bb", "bbb"],
                                }
                POST = Post()
            request = Request()

        model = DummyModel()
        model.assign(DummyRequestHandler())
        self.assertEqual(model.a, "aaa")
        self.assertEqual(model.d, ["b", "bb", "bbb"])

    def test_is_required(self):
        self.assertEqual(self.model.is_required("a"), True)
        self.assertEqual(self.model.is_required("b"), False)
