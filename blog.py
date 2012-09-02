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
import model, post, utils, config, post_handlers

class BlogModel(post.MasterPostModel):
    """Pagination for comments."""
    def default_pagination(self, cursor_str=""):
        self.pagination = utils.NextPrevPagination(
                model_cls=CommentModel,
                limit=config.get_config("blog_comments_per_page"),
                order="created",
                cursor_str=cursor_str,
                query=CommentModel.query(ancestor=self.key)
                )
        return self.pagination

class CommentModel(post.SlavePostModel):
    pass

class GuestAuthorModel(model.FormModel):
    """Model for comments of anonymous users."""
    display_name = ndb.StringProperty(verbose_name=_("Name"))
    email = ndb.StringProperty(verbose_name=_("Email"))
    website = ndb.StringProperty(verbose_name=_("Website"))

    def _validation(self):
        return {
                "display_name": {
                    "required": (),
                    },
                "email": {
                    "email": (),
                    "required": (),
                    },
                }

class BlogEditHandler(post_handlers.MasterPostEditHandler):
    def settings(self):
        return self._settings(model_cls=BlogModel, template="blog_edit", uri_id="blog-edit")

class BlogViewHandler(post_handlers.PostViewHandler):
    def settings(self):
        return self._settings(model_cls=BlogModel, slave_model_cls=CommentModel,
                template="blog_view", edit_uri_id="blog-edit")

    def _slave_pagination(self, post):
        return post.default_pagination(cursor_str=self.request.get("cursor"))

    def _additional_values(self, guest_author=None):
        return {
            "guest_comment_model": guest_author or GuestAuthorModel(),
            }

    def _post(self, slug=""):
        post = self._get_post_from_form()

        @ndb.transactional
        def comments():
            guest_author = None; comment = None
            guest_ok = True
            if not self.logged_in():
                guest_author = GuestAuthorModel(parent=post.key)
                guest_author.assign(self)
                if guest_author.validate():
                    guest_author.put()
                else: guest_ok = False
            author = guest_author.key if guest_author else self.get_current_user().key
            comment = CommentModel(parent=post.key, content=self.request.get("content"))
            if comment.validate() and guest_ok:
                comment.author = author
                comment.put()
                return None, None
            else:
                return guest_author, comment
        guest_author, comment = comments()
        self.render(self._template_name, self._render_values(post, slug, comment,
            additional_values=self._additional_values(guest_author)))
