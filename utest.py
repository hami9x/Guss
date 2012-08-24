import unittest
from google.appengine.ext import testbed

class TestCase(unittest.TestCase):
    def init_gae_stub(self, datastore):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        if datastore:
            self.testbed.init_datastore_v3_stub()

    def init_db_stub(self):
        self.init_gae_stub(datastore=True)
