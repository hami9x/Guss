import os
import webapp2
from webapp2_extras import i18n
import jinja2

class RequestHandler(webapp2.RequestHandler):
    jinjaEnv = jinja2.Environment(extensions=['jinja2.ext.i18n'],
            loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

    def __init__(self, *args, **kwds):
        self.jinjaEnv.install_gettext_translations(i18n, newstyle=True)
        webapp2.RequestHandler.__init__(self, *args, **kwds)

    def render(self, name, values={}):
        return self.jinjaEnv.get_template(name+".html").render(values)

