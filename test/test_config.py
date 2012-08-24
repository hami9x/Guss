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

from guss import utest, config

class TestUser(utest.TestCase):
    def setUp(self):
        self.init_db_stub()

    def test_update_get_config(self):
        config.update_config("testname", "testvalue", True)
        self.assertEqual("testvalue", config.get_config("testname"))

    def tearDown(self):
        self.testbed.deactivate()
