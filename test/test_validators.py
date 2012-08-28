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

from google.appengine.ext import ndb
from guss import utest, validators
from guss.validators import ValidationError as VE

class TestValidators(utest.TestCase):
    def setUp(self):
        self.init_db_stub()

    def test_word(self):
        validators.validate_word("dkk9fkk7_kk")
        self.assertRaises(VE, validators.validate_word, "*llkjkdf")

    def test_email(self):
        validators.validate_email("phaikawl@gmail.com")
        self.assertRaises(VE, validators.validate_email, "kkjkdfkkdf")
        self.assertRaises(VE, validators.validate_email, "@kdjkdf")
        self.assertRaises(VE, validators.validate_email, "dfkj**99@__")
        self.assertRaises(VE, validators.validate_email, "dfkj99@__")

    def test_password(self):
        validators.validate_password("kdkfk234")
        self.assertRaises(VE, validators.validate_password, "kkk")
        self.assertRaises(VE, validators.validate_password, "123")

    def test_min_length(self):
        validators.validate_min_length("123456789", 8)
        self.assertRaises(VE, validators.validate_min_length, "1234567", 8)

    def test_the_same(self):
        validators.validate_the_same("aaaa", "aaaa")
        self.assertRaises(VE, validators.validate_the_same, "kkkdf", "1111")

    def test_required(self):
        validators.validate_required("abc")
        self.assertRaises(VE, validators.validate_required, "")

    def test_unique(self):
        class DummyModel(ndb.Model):
            prop = ndb.StringProperty()
        mod = DummyModel(prop="abc")
        validators.validate_unique("abc", model=mod, field="prop")
        mod.put()
        validators.validate_unique("abc", model=mod, field="prop")  #still not raise error because
                                                                  ##the new model and the saved one are the same
        mod2 = DummyModel(prop="abc")
        self.assertRaises(VE, validators.validate_unique, "abc", mod2, field="prop")

    def test_integer(self):
        validators.validate_integer("123")
        self.assertRaises(VE, validators.validate_integer, "abc")
