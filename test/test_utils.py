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
from google.appengine.datastore.datastore_query import Cursor
from guss import utest, utils, post
import time

class TestUtils(utest.TestCase):
    def setUp(self):
        self.init_gae_stub(True, True)

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

    def test_next_prev_pagination(self):
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

    def test_numbered_pagination(self):
        class DummyMaster(post.MasterPostModel):
            pass
        class DummySlave(post.SlavePostModel):
            a = ndb.IntegerProperty()
        master = DummyMaster()
        master.put()
        pagination_new = lambda page: utils.NumberedPagination(model_cls=DummySlave,
                order="created",
                limit=5,
                page=page,
                master_key=master.key,
                )
        pagination = pagination_new(1)
        self.assertEqual(pagination.last_page_number(), 1)
        for i in range(utils.ATOMIC_PAGE_STEP):
            DummySlave(parent=master.key, a=i+1).put(pagination=pagination)
            clist = pagination.get_cursor_list()
            self.assertEqual(len(clist), 1)
        DummySlave(parent=master.key, a=6).put(pagination=pagination)
        clist = pagination.get_cursor_list()
        self.assertEqual(len(clist), 2)
        ents = DummySlave.query(ancestor=master.key).order(DummySlave.created) \
                .get(start_cursor=Cursor(urlsafe=clist[1]))
        self.assertEqual(ents.a, 6)

        for i in range(utils.ATOMIC_PAGE_STEP+1, 10):
            DummySlave(parent=master.key, a=i+1).put(pagination=pagination)
        pagination = pagination_new(1)
        self.assertEqual(len(pagination.items()), 5)
        self.assertEqual(pagination.items()[0].a, 1)
        pagination = pagination_new(2)
        self.assertEqual(len(pagination.items()), 5)
        self.assertEqual(pagination.items()[0].a, 6)
        self.assertEqual(pagination.last_page_number(), 2)

    def test_pagination_navi_generator(self):
        gen = utils.PaginationNaviGenerator(None)
        self.assertEqual([1, 2, 3], [i for i in gen.generate(5, 1, 3)])
        self.assertEqual([2, 5, 8, 9, 10], [i for i in gen.generate(5, 8, 10)])
        self.assertEqual([1, 5, 9, 12, 15], [i for i in gen.generate(5, 9, 16)])
        self.assertEqual(13, len([i for i in gen.generate(13, 2, 100)]))
