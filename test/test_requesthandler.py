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
