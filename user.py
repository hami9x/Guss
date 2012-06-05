import hashlib
from datetime import datetime, timedelta
from google.appengine.ext import db
from utils import generate_random_string

def generate_cookie_token():
    return generate_random_string(30)

def save_cookie(handler, username):
    token = generate_cookie_token()
    cookie_value = username + "|" + token
    expire = datetime.now() + timedelta(days=30)
    handler.response.set_cookie("_", cookie_value, expires = expire, httponly=True, overwrite=True)
    q = UserCookieModel.all().filter("username =", username).get()
    if not q:
        model = UserCookieModel(username=username, token=token)
        model.put()
    else:
        q.token = token
        q.put()

class UserInfo:
    def __init__(self, username, email):
        self.username = username
        self.email = email

def get_current_user(handler):
    username = handler.session.get("username", None)
    if username == None:
        value = handler.request.cookies.get("_", None)
        if value == None: return None
        l = value.split("|")
        username = l[0]
        token = l[1]
        q = UserCookieModel.all().filter("username =", username).get()
        if (not q) or (q.token != token):
            return None
        else:
            q = db.GqlQuery("SELECT email FROM UserModel WHERE username = :1", username).get()
            handler.session["username"] = username
            handler.session["email"] = q.email
            return UserInfo(username, q.email)
    else:
        return UserInfo(username, handler.session.get("email"))


class UserModel(db.Model):
    username = db.StringProperty()
    password = db.StringProperty()
    email = db.EmailProperty()
    created = db.DateTimeProperty(auto_now_add=True)
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
        q = db.GqlQuery("SELECT password, verified FROM UserModel WHERE username = :1",
                    self.username).get()
        if not q: return 0
        if (self.encrypt(self.password) == q.password):
            if q.verified:
                return 1
            else:
                return -1
        else: return 0

class UserCookieModel(db.Model):
    username = db.StringProperty()
    token = db.StringProperty()
