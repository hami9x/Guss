import unittest
from google.appengine.ext import testbed
from guss import rbac, user

#Role-based access control test case
class TestRBAC(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.user = user.UserModel(username="idiot", email="genius@gmail.com")
        self.user_key = self.user.put()

    def test_everything(self):
        parent_role_key = rbac.register_role("Employee")
        role_key = rbac.register_role("Boss", [parent_role_key])
        rbac.add_role(self.user_key, role_key)
        self.assertEqual(rbac.get_roles(self.user_key), [role_key])
        rbac.register_permission("access_acp", "Access the Admin CP")
        rbac.register_permission("another_perm", "An abitrary permission")
        rbac.allow(role_key, "access_acp")
        self.assertEqual(rbac.check_permission(self.user_key, "access_acp"), True)
        self.assertEqual(rbac.check_permission(self.user_key, "another_perm"), False)
        self.assertRaises(Exception, rbac.check_permission, self.user_key, "__DF_incorrect_perm___")
        #Now test to see if inheritance works
        rbac.allow(parent_role_key, "another_perm")
        self.assertEqual(rbac.check_permission(self.user_key, "another_perm"), True)
