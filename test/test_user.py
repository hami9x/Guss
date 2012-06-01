import unittest
from google.appengine.ext import testbed
from guss import user

class TestLogin(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        model = user.UserModel(nickname="testguy", password="testpass", email="testemail@gmail.com", verified=True)
        model.put();
        model = user.UserModel(nickname="unverifiedguy", password="testpass2",
                                    email="unverifiedguy@gmail.com", verified=False)
        model.put();

    def testLogin(self):
        self.assertEqual(1, user.login("testguy", "testpass"))
        self.assertEqual(0, user.login("testguy", "wrongpass"))
        self.assertEqual(0, user.login("wrongguy", "testpass"))
        self.assertEqual(-1, user.login("unverifiedguy", "testpass2"))

    def tearDown(self):
        testbed.deactivate()
