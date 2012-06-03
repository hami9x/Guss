import unittest
from google.appengine.ext import testbed
from guss import config

class TestUser(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def test_update_get_config(self):
        config.update_config("testname", "testvalue", True)
        self.assertEqual("testvalue", config.get_config("testname"))

    def tearDown(self):
        self.testbed.deactivate()
