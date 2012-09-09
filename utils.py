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

import random, string, re, urlparse, urllib, math
from unidecode import unidecode
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb
from google.appengine.api import memcache

def generate_random_string(length):
    return "".join(random.choice(string.ascii_letters + string.digits) for x in range(length))

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, delim=u"-"):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    result = unicode(delim.join(result))
    return "untitled" if not result else result

def cache_to_property(prop):
    def decorator(fn):
        def wrapper(obj, *args, **kwds):
            if not hasattr(obj, prop):
                setattr(obj, prop, fn(obj, *args, **kwds))
            return getattr(obj, prop)
        return wrapper
    return decorator

#TODO: test
class ObjectSettings(object):
    def __init__(self, **kwds):
        for k, v in kwds.items():
            setattr(self, k, v)

def page_url_modified(rhandler, name, val):
    """Return a new url with a specific param in the query string of current page modified."""
    full = urlparse.urlparse(rhandler.request.url)
    qdict = urlparse.parse_qs(full.query, True)
    if not isinstance(val, list): val = [val]
    qdict[name] = val
    full = (full[0], full[1], full[2], full[3], urllib.urlencode(qdict, True), full[5])
    return urlparse.urlunparse(full)

class Pagination(object):
    def items(self):
        return self._items

class NextPrevPagination(Pagination):
    def __init__(self, model_cls, limit, order, cursor_str="", query=None):
        cursor = Cursor(urlsafe=cursor_str) if cursor_str else Cursor()
        rcursor = cursor.reversed()
        cls_order = getattr(model_cls, order)
        if query == None: query = model_cls.query()
        q_forward = query.order(cls_order)
        q_reverse = query.order(-cls_order)
        self._items, self._next_cursor, self._more = q_forward.fetch_page(limit, start_cursor=cursor)
        unused_itemss, self._prev_cursor, unused_prev_more = q_reverse.fetch_page(limit, start_cursor=rcursor)
        self._cursor = cursor

    def has_next(self):
        return self._more

    def has_prev(self):
        return (self._cursor != Cursor()) and (self._prev_cursor != None)

    def next_cursor_str(self):
        return self._next_cursor.urlsafe() if self.has_next() else ""

    def prev_cursor_str(self):
        return self._prev_cursor.reversed().urlsafe() if self.has_prev() else ""

    def prev_page_url(self, requesthandler):
        return page_url_modified(requesthandler, "cursor", self.prev_cursor_str())

    def next_page_url(self, requesthandler):
        return page_url_modified(requesthandler, "cursor", self.next_cursor_str())

ATOMIC_PAGE_STEP = 5
class NumberedPagination(Pagination):
    """High-performance and super cost-effective pagination that could jump to a specific page, made for the forum.
    Of course with some rules:
        - Entities from the target model must not be actually deleted (should only mark as "deleted")
        - Entities must only be added at the end or beginning
    If these rules are broken, the pagination cannot work right.
    And a limitation: the page limit (number of items per page) are converted to a multiple of ATOMIC_PAGE_STEP,
    that means, for instance, ATOMIC_PAGE_STEP = 5 then limit=7 will be converted to 10, 12 converted to 15, etc.
    """
    def __init__(self, model_cls, limit, order, page, master_key):
        self.master_key = master_key
        limit = ((limit // ATOMIC_PAGE_STEP + 1) * ATOMIC_PAGE_STEP) if (limit % ATOMIC_PAGE_STEP != 0) else limit
        order = getattr(model_cls, order)
        self.query = model_cls.query(ancestor=master_key).order(order)
        clist = self._get_cursor_list().cursors
        self._last_page_number = int(math.ceil(float(len(clist)) / (limit // ATOMIC_PAGE_STEP)))
        if page<1:
            page = 1
        if page>self._last_page_number:
            page = self._last_page_number
        cursor = Cursor(urlsafe=clist[(page-1) * (limit // ATOMIC_PAGE_STEP)])
        self._items, unused_cursor, unused_more = self.query.fetch_page(limit, start_cursor=cursor)
        self.model_cls = model_cls
        self.limit = limit
        self.page = page

    def last_page_number(self):
        return self._last_page_number

    def slave_insert_hook(self, slave):
        self.master_update_cursors(slave)

    def master_update_cursors(self, slave):
        master = slave.key.parent().get()
        if master.key != self.master_key:
            raise Exception("The two masters must be the same.")
        if master.slave_count % ATOMIC_PAGE_STEP == 1:
            clist = self._get_cursor_list()
            if master.slave_count > 1:
                unused_list, next_cursor, unused_more = self.query.fetch_page(self.limit,
                        start_cursor=Cursor(urlsafe=clist.cursors[-1]))
                clist.cursors.append(next_cursor.urlsafe())
                clist.put()
                memcache.set(self.memcache_clist_keyname(), clist)

    def memcache_clist_keyname(self):
        return self.master_key.urlsafe()

    def get_cursor_list(self, get_obj=False):
        ret = memcache.get(self.memcache_clist_keyname(), None)
        if ret == None:
            clist = NumberedPaginationCursorModel.query(ancestor=self.master_key).fetch(2)
            if len(clist) > 1:
                raise Exception("There can be only 1 page cursor list.")
            if len(clist) == 0:
                    clist = NumberedPaginationCursorModel(cursors=[""], parent=self.master_key)
                    clist.put()
                    ret = clist
            else:
                ret = clist[0]
            memcache.set(self.memcache_clist_keyname(), ret)
        return ret if get_obj else ret.cursors

    def _get_cursor_list(self):
        if not hasattr(self, "_cursor_list"):
            self._cursor_list = self.get_cursor_list(get_obj=True)
        return self._cursor_list

    def navi_generate(self, *args, **kwds):
        return PaginationNaviGenerator(self)(*args, **kwds)

class NumberedPaginationCursorModel(ndb.Model):
    cursors = ndb.PickleProperty()

class PaginationNaviGenerator(object):
    def __init__(self, pagination):
        self._pagination = pagination

    """Generate page numbers for pagination, used in templates.
    Args:
        maximum_links: maximum number of links on the navigation, should be an odd number
    """
    def __call__(self, maximum_links):
        return self.generate(maximum_links, self._pagination.page, self._pagination.last_page_number())

    def generate(self, maximum_links, current, last):
        maximum = maximum_links-1 if (maximum_links % 2 != 0) else maximum_links-2
        maxim_before = maxim_after = maximum // 2
        if current-1 < maximum // 2:
            maxim_before = current-1
            maxim_after = maximum - maxim_before
        elif last-current < maximum //2:
            maxim_after = last-current
            maxim_before = maximum - maxim_after
        step = lambda start, stop, maxim: (abs(stop - start) // maxim) or 1
        if maxim_before:
            j = 0
            for i in reversed(range(current, 0, -step(current, 1, maxim_before))):
                if i!=current:
                    j += 1
                    if j>maxim_before: break
                    yield i
        yield current
        if maxim_after:
            j = 0
            for i in range(current, last+1, step(current, last, maxim_after)):
                if i!=current:
                    j += 1
                    if j>maxim_after: break
                    yield i
