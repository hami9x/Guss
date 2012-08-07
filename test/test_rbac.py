import unittest
from google.appengine.ext import testbed
from guss import rbac, user, install

#Role-based access control test case
class TestRBAC(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        install.install_rbac();
        self.user = user.UserModel(username="idiot", email="genius@gmail.com")
        self.user_key = self.user.put(force_validation=False)

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
        #Now check the check_permission of multiple perms
        rbac.register_permission("troll", "Troll")
        rbac.allow(role_key, "troll")
        self.assertEqual(rbac.check_permission(self.user_key, ["troll", "access_acp"]), True)
        self.assertEqual(rbac.check_permission(self.user_key, ["access_acp", "another_perm"]), False)

        #Now test inheritance
        rbac.allow(parent_role_key, "another_perm")
        self.assertEqual(rbac.check_permission(self.user_key, "another_perm"), True)

        #Test the special Super Admin role
        super_admin = rbac.default_role("super_admin")
        self.assertEqual(super_admin.id(), "super_admin")
        new_user = user.UserModel(username="genius", email="idiot@gmail.com")._put()
        rbac.add_role(new_user, super_admin)
        self.assertEqual(rbac.check_permission(self.user_key, "access_acp"), True)
        self.assertEqual(rbac.check_permission(new_user, "another_perm"), True)
