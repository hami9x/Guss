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
from webapp2_extras.i18n import _lazy as _
import model
import utils

class BlogModel(model.FormModel):
    author = ndb.KeyProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    title = ndb.StringProperty(verbose_name=_("Title"))
    content = ndb.TextProperty(verbose_name=_("Content"))
    slug = ndb.StringProperty()

    def display_author(self):
        return self.author.get().username

    def display_created(self):
        return "%d/%d/%d" % (self.created.day, self.created.month, self.created.year)

    def _validation(self):
        return {
                "title": {
                    "max_length": (120,),
                    "required": (),
                    },
                }

    def make_slug(self):
        self.slug = utils.slugify(self.title)
        count = BlogModel.query(BlogModel.slug == self.slug).count()
        if count > 0:
            self.slug += "-%d" % (count+1)
