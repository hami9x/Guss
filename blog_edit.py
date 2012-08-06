from webapp2_extras.i18n import _
from requesthandler import RequestHandler
from blog import BlogModel
import utils

class BlogEditHandler(RequestHandler):
    def __init__(self, *args, **kwds):
        super(BlogEditHandler, self).__init__(*args, **kwds)

    def _check_permission(self):
        return (
                    (   self.current_user_check_permission("edit_own_blog")
                        and
                        self.logged_in() and (self.get_current_user().key == self._blog.author)
                    )
                    or self.current_user_check_permission("edit_all_blog")
                )

    def _handler_init(self, slug=""):
        self._blog_slug = slug
        blogid = self.request.get("blogid")
        def fn_invalid():
            self.response.out.write(self.render("noticepage", {
                "message": _(u"This blog post does not exist."),
                }))
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
                self._blog.author = self.get_current_user().key
        self._blogid = blogid


    def _get(self):
        values = {
                "model": self._blog,
                "blogid": self._blogid,
                }
        self.response.out.write(self.render("blog_edit", values))

    def _post(self):
        blog = self._blog
        blog.assign(self)
        if blog.validate():
            if not blog.slug:
                blog.slug = utils.slugify(blog.title)
                count = BlogModel.query(BlogModel.slug == blog.slug).count()
                if count > 0:
                    blog.slug += "-%d" % (count+1)
            blog.put()

        values = {
                "model": blog,
                "blogid": self._blogid,
                }
        if not self._blog_slug:
            self.redirect(self.uri_for("blog-edit", slug=blog.slug))
        else:
            self.response.out.write(self.render("blog_edit", values))
