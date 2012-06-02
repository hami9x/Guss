import hashlib
from gettext import gettext as _
import webapp2
from google.appengine.ext import db
from requesthandler import RequestHandler
import logging

class UserModel(db.Model):
    nickname = db.StringProperty()
    password = db.StringProperty()
    email = db.EmailProperty()
    verified = db.BooleanProperty()

    def __init__(self, *args, **kwds):
        super(UserModel, self).__init__(*args, **kwds)
        if self.password != None:
            self.password = self.encrypt(self.password)

    @staticmethod
    def encrypt(str):
        m = hashlib.sha224()
        m.update(str)
        return m.hexdigest()

    def login(self):
        q = db.GqlQuery("SELECT password, verified FROM UserModel WHERE nickname = :1",
                    self.nickname).get()
        if not q: return 0
        if (self.encrypt(self.password) == q.password):
            if q.verified:
                return 1
            else:
                return -1
        else: return 0


class LoginHandler(RequestHandler):
    def get(self):
        successful = self.request.get("successful", None)
        if successful == None:
            self.response.out.write(self.render("loginpage"))
        else:
            if successful == 1:
                values = {
                        "message": _("You successfully signed in, welcome back!"),
                        "redirect": self.request.headers.get("Referer", "/"),
                        }
            elif successful == 0:
                values = {
                        "message": _("Login failed, user doesn't exists, you could try again."),
                        "redirect": self.request.headers.get("/user/login", "/"),
                        }
            else:
                values = {
                        "message": _("The user is valid but not verified,\
                                check your email to find the confirmation link\
                                we sent to you when you registered."),
                        "redirect": None,
                        }
            self.response.out.write(self.render("noticepage", values))

    def post(self):
        nickname = self.request.get("nickname")
        password = self.request.get("password")
        model = UserModel(nickname=nickname, password=password)
        login = model.login()
        return webapp2.redirect("/user/login?successful=%s" % str(login))
