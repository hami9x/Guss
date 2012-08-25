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

import random
import string
import re
from unidecode import unidecode
from google.appengine.datastore.datastore_query import Cursor

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

class NextPrevPagination(object):
    def __init__(self, model_cls, limit, order, cursor_str=""):
        cursor = Cursor(urlsafe=cursor_str) if cursor_str else Cursor()
        rcursor = cursor.reversed()
        cls_order = getattr(model_cls, order)
        q_forward = model_cls.query().order(cls_order)
        q_reverse = model_cls.query().order(-cls_order)
        self._items, self._next_cursor, self._more = q_forward.fetch_page(limit, start_cursor=cursor)
        unused_itemss, self._prev_cursor, unused_prev_more = q_reverse.fetch_page(limit, start_cursor=rcursor)
        self._cursor = cursor

    def items(self):
        return self._items

    def has_next(self):
        return self._more

    def has_prev(self):
        return (self._cursor != Cursor()) and (self._prev_cursor != None)

    def next_cursor_str(self):
        return self._next_cursor.urlsafe() if self.has_next() else ""

    def prev_cursor_str(self):
        return self._prev_cursor.reversed().urlsafe() if self.has_prev() else ""
