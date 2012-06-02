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
        self.assertEqual(1, user.UserModel(nickname="testguy", password="testpass").login())
        self.assertEqual(0, user.UserModel(nickname="testguy", password="wrongpass").login())
        self.assertEqual(0, user.UserModel(nickname="wrongguy", password="testpass").login())
        self.assertEqual(-1, user.UserModel(nickname="unverifiedguy", password="testpass2").login())

    def tearDown(self):
        self.testbed.deactivate()
