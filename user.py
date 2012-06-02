import hashlib
from datetime import datetime, timedelta
from google.appengine.ext import db
from utils import generate_random_string

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

