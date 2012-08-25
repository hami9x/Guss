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
import post
import utils
import config

class BlogModel(post.MasterPostModel):
    def get_slaves_pagination(self, cursor_str):
        if not hasattr(self, "_slaves_pagin"):
            self._slaves_pagin = utils.NextPrevPagination(
                    model_cls=CommentModel,
                    limit=int(config.get_config("blog_comments_per_page")),
                    order="created",
                    cursor_str=cursor_str,
                    query=CommentModel.query(ancestor=self.key)
                    )
            return self._slaves_pagin
        else:
            return self._slaves_pagin

class CommentModel(post.SlavePostModel):
    pass

class GuestAuthorModel(post.SlavePostModel):
    """Model for comments of anonymous users."""
    username = ndb.StringProperty(verbose_name=_("Name"))
    email = ndb.StringProperty(verbose_name=_("Email"))
    website = ndb.StringProperty(verbose_name=_("Website"))

    def _validation(self):
        return {
                "username": {
                    "required": (),
                    },
                "email": {
                    "email": (),
                    "required": (),
                    },
                }
