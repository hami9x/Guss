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

class TestCase(unittest.TestCase):
    def init_gae_stub(self, datastore=True, memcache=False):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        if datastore:
            self.testbed.init_datastore_v3_stub()
        if memcache:
            self.testbed.init_memcache_stub()

    def init_db_stub(self):
        self.init_gae_stub(datastore=True)
