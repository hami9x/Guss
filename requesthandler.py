import os
import webapp2
from webapp2_extras import i18n, sessions
import jinja2
import user
import config

class JinjaEnv(jinja2.Environment):
    def __init__(self):
        super(JinjaEnv, self).__init__(
            extensions=['jinja2.ext.i18n'],
            loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"))
            )
        self.install_gettext_translations(i18n, newstyle=True)
        self.globals["getattr"] = getattr

    def render(self, name, values={}):
        return self.get_template(name+".html").render(values)

class RequestHandler(webapp2.RequestHandler):
    def __init__(self, *args, **kwds):
        self.template = JinjaEnv()
        webapp2.RequestHandler.__init__(self, *args, **kwds)

    def get_config(self, key): config.get_config(key)
    def update_config(self, *args, **kwds): config.update_config(*args, **kwds)

    def render(self, *args, **kwds):
        return self.template.render(*args, **kwds)

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    #Map the function in user module to this class for convenience
    def get_current_user(self):
        return user.get_current_user(self)
