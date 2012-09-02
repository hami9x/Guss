from google.appengine.ext import ndb
from webapp2_extras.i18n import _lazy as _
import model, utils

class PostModel(model.FormModel):
    """Common base for all kinds of user content, including blog, forum posts, comments..."""
    author = ndb.KeyProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    content = model.EscapedHtmlProperty(verbose_name=_("Content"))

    def display_author(self):
        q = self.author.get()
        return q.display_name or q.username

    def display_created(self):
        return "%d/%d/%d" % (self.created.day, self.created.month, self.created.year)

class MasterPostModel(PostModel):
    """Base class for posts that make a new "topic", such as blog entries, and the forum posts that starts a thread."""
    title = ndb.StringProperty(verbose_name=_("Title"))
    slug = ndb.StringProperty()
    slave_count = ndb.IntegerProperty(default=0)
    content = model.FilteredHtmlProperty(verbose_name=_("Content"))

    """Pagination for slaves."""
    def default_pagination(self):
        raise Exception("")

    def _validation(self):
        return {
                "title": {
                    "max_length": (120,),
                    "required": (),
                    },
                }

    def make_slug(self):
        self.slug = utils.slugify(self.title)
        count = self.__class__.query(self.__class__.slug == self.slug).count()
        if count > 0:
            self.slug += "-%d" % (count+1)


class SlavePostModel(PostModel):
    """Base class for things like comments, forum replies..."""
    def _validation(self):
        return {
                "content": {
                    "required": (),
                    }
                }

    @ndb.transactional
    def put(self, master=None, pagination=None, *args, **kwds):
        super(SlavePostModel, self).put(*args, **kwds);
        master = master or self.key.parent().get()
        master.slave_count += 1
        master.put()
        if pagination: pagination.slave_insert_hook(self)
