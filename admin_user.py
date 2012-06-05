from google.appengine.ext import db
from webapp2_extras.i18n import _
from requesthandler import RequestHandler
import user
import user_confirm

#User management page
class AdminUserHandler(RequestHandler):
    DEFAULT_LIMIT = 20
    DEFAULT_ORDER = "created"
    def get(self):
        try:
            limit = int(self.request.get("limit", self.DEFAULT_LIMIT))
        except ValueError:
            limit = self.DEFAULT_LIMIT
        order = self.request.get("order", self.DEFAULT_ORDER)
        if not (order in ["username", "email", "created"]):
            order = self.DEFAULT_ORDER
        q = db.GqlQuery("SELEcT * FROM UserModel ORDER BY %s DESC LIMIT %d" % (order, limit))
        values = {
                "users": q,
                }
        self.response.out.write(self.render("admin_user", values))

class AdminAddUserHandler(RequestHandler):
    def get(self):
        self.response.out.write(self.render("admin_user_add"))

    def post(self):
        username = self.request.get("username")
        email = self.request.get("email")
        model = user.UserModel(username=username, email=email, verified=False)
        model.put()
        user_confirm.send_confirmation_mail(self, username, email)
        values = {
                "message": _("An email has been sent to you that contains the link to activate your account, \
                                check your mail box."),
                "redirect": None,
                }
        self.response.out.write(self.render("noticepage", values))
