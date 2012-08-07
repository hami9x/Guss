from google.appengine.ext import ndb
from webapp2_extras.i18n import _
from user import UserModel
import user_confirm
import admin
import config
import rbac

#User management page
class AdminUserHandler(admin.AdminRequestHandler):
    DEFAULT_LIMIT = 20
    DEFAULT_ORDER = "created"
    def _get(self):
        try:
            limit = int(self.request.get("limit", self.DEFAULT_LIMIT))
        except ValueError:
            limit = self.DEFAULT_LIMIT
        order = self.request.get("order", self.DEFAULT_ORDER)
        if not (order in ["username", "email", "created"]):
            order = self.DEFAULT_ORDER
        q = ndb.gql("SELEcT * FROM UserModel ORDER BY %s DESC LIMIT %d" % (order, limit))
        values = {
                "users": q,
                "user_add_url": self.uri_for("add-user")
                }
        self.response.out.write(self.render("admin_user", values))

class AdminAddUserHandler(admin.AdminRequestHandler):
    def _get(self):
        model = UserModel()
        self.response.out.write(self.render("admin_user_add", {"model": model}))

    def _post(self):
        username = self.request.get("username")
        email = self.request.get("email")
        model = UserModel(verified=False)
        model.assign(self)
        if model.validate():
            if config.get_config("user_email_confirm") == "yes":
                model.put()
                user_confirm.send_confirmation_mail(username, email)
                values = {
                        "message": _(u"""An email that contains the link to activate the account \
                            has been sent to the email"""),
                        "redirect": None,
                        }
                self.response.out.write(self.render("noticepage", values))
            else:
                model.verified = True
                user_key = model.put()
                rbac.add_role(user_key, rbac.default_role("registered"))
                values = {
                        "message": _(u"""Successfully registered."""),
                        "redirect": None,
                        }
                self.response.out.write(self.render("noticepage", values))
        else:
            values = {
                    "model": model
                    }
            self.response.out.write(self.render("admin_user_add", values))
