import unittest
from google.appengine.ext import db
from google.appengine.ext import testbed
import guss.user

class TestLogin(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()


