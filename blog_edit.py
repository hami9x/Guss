from webapp2_extras.i18n import _
from requesthandler import RequestHandler
from blog import BlogModel
import utils

class BlogEditHandler(RequestHandler):
    def __init__(self, blog_slug):
        super(BlogEditHandler, self).__init__
        self._blog_slug = blog_slug

    def _check_permission(self):
        return ( self.current_user_check_permission("edit_own_blog")
                    and
                 self.get_current_user().key == self.blog.author
                ) or self.current_user_check_permission("edit_all_blog")

    def _get(self):
        if self._blog_slug == "":
            blog = BlogModel(title="", content="")
            blogid = None
        else:
            blog = BlogModel.query(BlogModel.slug == self._blog_slug).get()
            if blog == None:
                return self.response.out.write(self.render("noticepage", {
                    "message": _(u"This blog post does not exist."),
                    }))
            blogid = blog.key.id()

        values = {
                "model": blog,
                "blogid": blogid,
                }
        self.response.out.write(self.render("blog_edit.html", values))

    def _post(self):
        blogid = self.request.get("id", "")
        if blogid:
            blog = BlogModel.get_by_id(blogid)
        else:
            blog = BlogModel()
            blog.author = self.get_current_user().key
        blog.assign(self)
        if blog.validate():
            blog.slug = utils.slugify(blog.title)
            count = BlogModel.query(BlogModel.slug == blog.slug).count()
            if count > 0:
                blog.slug += "-%d" % (count+1)
            blog.put()

        values = {
                "model": blog,
                "blogid": blogid,
                }
        self.response.out.write(self.render("blog_edit.html", values))
