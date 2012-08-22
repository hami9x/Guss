# Copyright 2012 Hai Thanh Nguyen
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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

class DummyChild(DummyModel):
    c = ndb.StringProperty()
    def _validation(self):
        return {
                "c": {"required": ()},
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

        c = DummyChild(c="df", a="")
        self.assertEqual(c.validate(), False)
        c = DummyChild(c="df", a="kkdf", b="dfdf")
        self.assertEqual(c.validate(), True)

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
