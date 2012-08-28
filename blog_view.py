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
from webapp2_extras.i18n import _
from requesthandler import RequestHandler
import blog, blog_edit
from blog import BlogModel

class BlogViewHandler(RequestHandler):
    def _check_permission(self):
        return self.current_user_check_permission("view_blog")

    def _render_view(self, post, slug, comment_model=None, guest_comment_model=None):
        """Don't-Repeat-Yourself helper"""
        return self.render("blog_view", {
            "model": post,
            "can_edit": lambda: blog_edit.can_user_edit_post(self, post),
            "edit_url": self.uri_for("blog-edit", slug=slug),
            "comments_pagin": post.get_slaves_pagination(self.request.get("cursor")),
            "comment_model": comment_model or blog.CommentModel(),
            "guest_comment_model": guest_comment_model or blog.GuestAuthorModel(),
            })

    def _get(self, slug=""):
        blg = BlogModel.query(BlogModel.slug == slug).get()
        if blg == None:
            return self.render("noticepage", {
                "message": _(u"This blog post does not exist."),
                })
        else:
            self._render_view(blg, slug)

    def _post(self, slug=""):
        post = BlogModel.get_by_id(int(self.request.get("__master")))
        @ndb.transactional
        def comments():
            guest_author = None; comment = None
            guest_ok = True
            if not self.logged_in():
                guest_author = blog.GuestAuthorModel(parent=post.key)
                guest_author.assign(self)
                if guest_author.validate():
                    guest_author.put()
                else: guest_ok = False
            author = guest_author.key if guest_author else self.get_current_user().key
            comment = blog.CommentModel(parent=post.key, content=self.request.get("content"))
            if comment.validate() and guest_ok:
                comment.author = author
                comment.put()
                return None, None
            else:
                return guest_author, comment
        guest_author, comment = comments()
        self._render_view(post, slug, comment, guest_author)
