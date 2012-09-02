from webapp2_extras.i18n import _lazy as _
from google.appengine.ext import ndb
import model, post, post_handlers, utils, config

class ThreadModel(post.MasterPostModel):
    def default_pagination(self, page=1):
        self.pagination = utils.NumberedPagination(model_cls=ReplyModel,
                limit=config.get_config("forum_replies_per_page"),
                order="created",
                page=page,
                master_key=self.key
                )
        return self.pagination

class ReplyModel(post.SlavePostModel):
    content = model.FilteredHtmlProperty(verbose_name=_("Content"))

class CategoryModel(model.FormModel):
    name = ndb.StringProperty(verbose_name=_("Name"))
    direct_parent = ndb.KeyProperty()

class ForumThreadEditHandler(post_handlers.MasterPostEditHandler):
    def settings(self):
        return self._settings(model_cls=ThreadModel, template="forumthread_edit", uri_id="forumthread-edit")

class ForumThreadViewHandler(post_handlers.PostViewHandler):
    def settings(self):
        return self._settings(model_cls=ThreadModel, slave_model_cls=ReplyModel,
                template="forumthread_view", edit_uri_id="forumthread-edit")

    def _slave_pagination(self, post):
        try:
            page = int(self.request.get("page"))
        except ValueError:
            page = 1
        return post.default_pagination(page=page)

    def _post(self, slug=""):
        post = self._get_post_from_form()
        reply = self._slave_model_cls(parent=post.key, author=self.get_current_user().key)
        reply.assign(self)
        if reply.validate():
            reply.put(master=post, pagination=self._slave_pagination(post))
            reply = self._slave_model_cls()
        self.render(self._template_name, self._render_values(post, slug, reply))
