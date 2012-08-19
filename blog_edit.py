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

from webapp2_extras.i18n import _
from requesthandler import RequestHandler
from blog import BlogModel

def can_user_edit_post(handler, model):
    return (
            (   handler.current_user_check_permission("edit_own_blog")
                and (handler.get_current_user().key == model.author)
            )
            or handler.current_user_check_permission("edit_all_blog")
        )

class BlogEditHandler(RequestHandler):
    def __init__(self, *args, **kwds):
        super(BlogEditHandler, self).__init__(*args, **kwds)

    def _check_permission(self):
        return can_user_edit_post(self, self._blog)

    def _handler_init(self, slug=""):
        self._blog_slug = slug
        blogid = self.request.get("blogid")
        def fn_invalid():
            self.render("noticepage", {
                "message": _(u"This blog post does not exist."),
                })
            self.stop()

        if blogid:
            self._blog = BlogModel.get_by_id(blogid)
            if self._blog == None:
                return fn_invalid()
        else:
            if self._blog_slug:
                self._blog = BlogModel.query(BlogModel.slug == self._blog_slug).get()
                if self._blog == None:
                    return fn_invalid()
                blogid = self._blog.key.id()
            else:
                self._blog = BlogModel(title="", content="")
                if self.logged_in():
                    self._blog.author = self.get_current_user().key
        self._blogid = blogid


    def _get(self, *args, **kwds):
        values = {
                "model": self._blog,
                "blogid": self._blogid,
                }
        return self.render("blog_edit", values)

    def _post(self, *args, **kwds):
        blog = self._blog
        blog.assign(self)
        if blog.validate():
            if not blog.slug:
                blog.make_slug()
                blog.put()

        values = {
                "model": blog,
                "blogid": self._blogid,
                }
        if not self._blog_slug:
            self.redirect(self.uri_for("blog-edit", slug=blog.slug))
        else:
            return self.render("blog_edit", values)
