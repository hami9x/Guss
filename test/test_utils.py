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

from google.appengine.ext import ndb
from guss import utest, utils
import time

class TestUtils(utest.TestCase):
    def setUp(self):
        self.init_db_stub()

    def test_slugify(self):
        self.assertEqual(utils.slugify(u"abc đè"), "abc-de")
        self.assertEqual(utils.slugify("^^^"), "untitled")

    def test_page_url_modified(self):
        class DummyHandler(object):
            def __init__(self):
                self.request = lambda: None
                self.request.url = "http://guco.dz?ok=False"
        h = DummyHandler()
        self.assertEqual(utils.page_url_modified(h, "ok", "True"), "http://guco.dz?ok=True")
        self.assertEqual(utils.page_url_modified(h, "cursor", "ZZZ"), "http://guco.dz?cursor=ZZZ&ok=False")

    def test_pagination(self):
        class DummyModel(ndb.Model):
            created = ndb.DateTimeProperty(auto_now_add=True)
            num = ndb.IntegerProperty()
        for i in range(20):
            m = DummyModel(num=i)
            m.put()
            time.sleep(0.05)
        pagin = utils.NextPrevPagination(model_cls=DummyModel,
                order="created",
                limit=10
                )
        self.assertEqual(len(pagin.items()), 10)
        self.assertEqual(pagin.items()[0].num, 0)
        self.assertEqual(pagin.prev_cursor_str(), "")
        self.assertEqual(pagin.has_prev(), False)
        ncursor = pagin.next_cursor_str()
        self.assertEqual(pagin.has_next(), True)
        self.assertNotEqual(ncursor, "")
        pagin2 = utils.NextPrevPagination(model_cls=DummyModel,
                order="created",
                limit=10,
                cursor_str=ncursor)
        self.assertEqual(pagin2.items()[0].num, 10)
        self.assertEqual(pagin2.has_prev(), True)
        pcursor = pagin2.prev_cursor_str()
        self.assertNotEqual(pcursor, "")
        pagin3 = utils.NextPrevPagination(model_cls=DummyModel,
                order="created",
                limit=10,
                cursor_str=pcursor)
        self.assertEqual(pagin3.items()[0].num, 0)
