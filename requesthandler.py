import os
import webapp2
from webapp2_extras import i18n, sessions
from webapp2_extras.i18n import _lazy as _
import jinja2
import user
import config
import rbac
import inspect

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
        self._stop = False
        self._template = JinjaEnv()
        webapp2.RequestHandler.__init__(self, *args, **kwds)

    def get_config(self, key): config.get_config(key)
    def update_config(self, *args, **kwds): config.update_config(*args, **kwds)

    def render(self, *args, **kwds):
        return self._template.render(*args, **kwds)

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

    def get_current_user(self):
        """Get the current user"""
        try:
            _gabage = self._current_user
        except AttributeError:
            self._current_user = user.get_current_user(self)
        return self._current_user

    def logged_in(self):
        return self.get_current_user() != None

    def _get(self):
        """To be overridden"""
        pass

    def _post(self):
        """To be overridden"""
        pass

    def _check_permission(self):
        """To be overridden. This method performs the specific permission checking of a child class.
        Must return True or False."""
        return True

    def _handler_init(self, *args, **kwds):
        """To be overridden. This method performs the initialization that runs at the beginning of post() or get()"""
        pass

    def get(self, *args, **kwds):
        self._handler_init(*args, **kwds)
        self.check_permission(self._get)

    def post(self, *args, **kwds):
        self._handler_init(*args, **kwds)
        self.check_permission(self._post)

    def _check_permission_hierarchy(self):
        """Check permission of the object and all its ancestors.
        To allow the access, all permission requirements of the object's ascendants must be fulfilled.
        """
        hierarchy = inspect.getmro(type(self))
        for cls in hierarchy:
            try:
                if cls._check_permission(self) == False:
                    return False
            except AttributeError:
                pass
        return True


    def check_permission(self, fn):
        """Performs page-level permission checking."""
        if self._check_permission_hierarchy():
            if not self._stop: fn()
        else:
            values = {
                    "message": _(u"You are not allowed to access this page."),
                    "redirect": None,
                    }
            self.response.out.write(self.render("noticepage", values))

    def current_user_check_permission(self, perms):
        if self.get_current_user() == None:
            return rbac.check_permission_role(rbac.default_role("guest"), perms)
        else:
            return rbac.check_permission(self.get_current_user().key, perms)

    def rbac_check_permission(self, user, perms):
        return rbac.check_permission(user, perms)

    def stop(self):
        self._stop = True
