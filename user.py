import hashlib
from datetime import datetime, timedelta
from gettext import gettext as _
from google.appengine.ext import db
from requesthandler import RequestHandler
from utils import generate_random_string

def get_login_url():
    return "/user/login"

def generate_cookie_token():
    return generate_random_string(30)

def save_cookie(handler, nickname):
    token = generate_cookie_token()
    cookie_value = nickname + "|" + token
    expire = datetime.now() + timedelta(days=30)
    handler.response.set_cookie("_", cookie_value, expires = expire, httponly=True, overwrite=True)
    q = UserCookieModel.all().filter("nickname =", nickname).get()
    if not q:
        model = UserCookieModel(nickname=nickname, token=token)
        model.put()
    else:
        q.token = token
        q.put()

class UserInfo:
    def __init__(self, nickname, email):
        self.nickname = nickname
        self.email = email

def get_current_user(handler):
    nickname = handler.session.get("nickname", None)
    if nickname == None:
        value = handler.request.cookies.get("_", None)
        if value == None: return None
        l = value.split("|")
        nickname = l[0]
        token = l[1]
        q = UserCookieModel.all().filter("nickname =", nickname).get()
        if (not q) or (q.token != token):
            return None
        else:
            q = db.GqlQuery("SELECT email FROM UserModel WHERE nickname = :1", nickname).get()
            handler.session["nickname"] = nickname
            handler.session["email"] = q.email
            return UserInfo(nickname, q.email)
    else:
        return UserInfo(nickname, handler.session.get("email"))


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
        m = hashlib.sha512()
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

class UserCookieModel(db.Model):
    nickname = db.StringProperty()
    token = db.StringProperty()

class LoginHandler(RequestHandler):
    def get(self):
        successful = self.request.get("successful", None)
        render_notice = lambda values: self.response.out.write(self.render("noticepage", values))
        if successful == "1":
            values = {
                    "message": _("You successfully signed in, welcome back!"),
                    "redirect": self.request.get("referer"),
                    }
            render_notice(values)
        elif successful == "0":
            values = {
                    "message": _("Login failed, user doesn't exists, you could try again."),
                    "redirect": get_login_url(),
                    }
            render_notice(values)
        elif successful == "-1":
            values = {
                    "message": _("The user is valid but not verified,\
                            check your email to find the confirmation link\
                            we sent to you when you registered."),
                    "redirect": None,
                    }
            render_notice(values)
        else:
            values = { "referer": self.request.headers.get("Referer", "/") }
            self.response.out.write(self.render("loginpage", values))

    def post(self):
        nickname = self.request.get("nickname")
        password = self.request.get("password")
        referer = self.request.get("referer")
        model = UserModel(nickname=nickname, password=password)
        login = model.login()
        if login == 1:
            save_cookie(self, nickname)
        return self.redirect(get_login_url()+"?successful=%s&referer=%s" % (str(login), referer))
