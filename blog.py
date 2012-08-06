from google.appengine.ext import ndb
from webapp2_extras.i18n import _lazy as _
import model
import utils

class BlogModel(model.FormModel):
    author = ndb.KeyProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    title = ndb.StringProperty(verbose_name=_("Title"))
    content = ndb.TextProperty(verbose_name=_("Content"))
    slug = ndb.StringProperty()

    def _validation(self):
        return {
                "title": {
                    "max_length": (120,),
                    "required": (),
                    },
                }

    def make_slug(self):
        self.slug = utils.slugify(self.title)
        count = BlogModel.query(BlogModel.slug == self.slug).count()
        if count > 0:
            self.slug += "-%d" % (count+1)
