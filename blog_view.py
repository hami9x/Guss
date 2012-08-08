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
