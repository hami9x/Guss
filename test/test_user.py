import webapp2
import unittest
from google.appengine.ext import testbed
from google.appengine.ext import ndb
from guss import user

class TestUser(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        model = user.UserModel(username="testguy", password="testpass1", email="testemail@gmail.com", verified=True)
        self.testguy_key = model.put(force_validation=False);
        model = user.UserModel(username="unverifiedguy", password="testpass2",
                                    email="unverifiedguy@gmail.com", verified=False)
        model.put(force_validation=False);

    def test_login(self):
        self.assertEqual(0, user.UserModel(username="testguy", password="wrongpass").login())
        self.assertEqual(0, user.UserModel(username="wrongguy", password="testpass").login())
        self.assertEqual(-1, user.UserModel(username="unverifiedguy", password="testpass2").login())

        self.assertEqual(1, user.UserModel(username="testguy", password="testpass1").login())
        #Test cookie save
        request = webapp2.RequestHandler()
        request.response = webapp2.Response()
        user.save_cookie(request, self.testguy_key)
        q = ndb.Key("UserCookieModel", self.testguy_key.id()).get()
        self.assertTrue(q and (len(q.token) > 0))

    def tearDown(self):
        self.testbed.deactivate()
