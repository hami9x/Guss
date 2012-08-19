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
from google.appengine.ext import testbed
from guss import user, rbac
from guss.requesthandler import RequestHandler
import install
class Data:
    @classmethod
    def init(cls):
        cls.admin = user.UserModel(username="genius", email="idiot@gmail.com").put(force_validation=False)
        cls.admin_role = rbac.default_role("admin")
        rbac.add_role(cls.admin, cls.admin_role)
        rbac.register_permission("troll", "Trolling")
        rbac.register_permission("joke", "Make joke")
        rbac.register_permission("spam", "Spamming")
        rbac.allow(cls.admin_role, "joke")

##Start## Permission dummy classes ####
class DummyParent(RequestHandler):
    def _check_permission(self):
        return self.rbac_check_permission(Data.admin, ["troll"])

class DummyChild_Faulty(DummyParent):
    def _check_permission(self):
        return self.rbac_check_permission(Data.admin, ["joke"])

class DummyChild_OK(DummyParent):
    def _check_permission(self):
        rbac.allow(Data.admin_role, "troll")
        #return self.rbac_check_permission(Data.admin, ["joke", "troll"])
        return rbac.check_permission(Data.admin, "joke")
##End## Permission dummy classes ####

class Dummy(RequestHandler):
    def _handler_init(self):
        self.a = "123"

    def _get(self):
        assert self.a == "123"

class RequestHandlerTest(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        install.install_rbac()
        Data.init()

    def test_permission(self):
        fchild = DummyChild_Faulty()
        self.assertEqual(fchild._check_permission_hierarchy(), False)
        ochild = DummyChild_OK()
        self.assertEqual(ochild._check_permission_hierarchy(), True)

    def test_method_order(self):
        d = Dummy()
        d.get()
