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
import blog_edit
from blog import BlogModel

class BlogViewHandler(RequestHandler):
    def _check_permission(self):
        return self.current_user_check_permission("view_blog")

    def _get(self, slug=""):
        blg = BlogModel.query(BlogModel.slug == slug).get()
        if blg == None:
            return self.render("noticepage", {
                "message": _(u"This blog post does not exist."),
                })
        else:
            return self.render("blog_view", {
                "model": blg,
                "can_edit": lambda: blog_edit.can_user_edit_post(self, blg),
                "edit_url": self.uri_for("blog-edit", slug=slug),
                })
