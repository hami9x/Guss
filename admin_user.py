from google.appengine.ext import db
from requesthandler import RequestHandler
import user

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
        if not (order in ["nickname", "email", "created"]):
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
        nickname = self.request.get("nickname")
        email = self.request.get("email")
        model = user.UserModel(nickname=nickname, email=email, verified=False)
        model.put()
