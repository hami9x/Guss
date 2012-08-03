import hashlib
from datetime import datetime, timedelta
from google.appengine.ext import ndb
from utils import generate_random_string
from webapp2_extras.i18n import _lazy as _
import model

class UserModel(model.FormModel):
    username = ndb.StringProperty(verbose_name=_(u"Username"))
    password = ndb.StringProperty(verbose_name=_(u"Password"))
    email = ndb.StringProperty(verbose_name=_(u"Email"))
    created = ndb.DateTimeProperty(auto_now_add=True)
    verified = ndb.BooleanProperty()
    _password_confirm = model.UnsavedProperty(verbose_name=_(u"Confirm password"))

    def __init__(self, *args, **kwds):
        super(UserModel, self).__init__(*args, **kwds)
        if self.password != None:
            self.password = self.encrypt(self.password)

    def _validation(self):
        return {
                "username": {"required": (), "word": (), "unique": ()},
                "email": {"required": (), "email": (), "unique": ()},
                "password": {"required": (), "password": (), "min_length": (8,)},
                "_password_confirm": {"required": (), "confirm_password": (self.password,)},
                }

    @staticmethod
    def encrypt(str):
        m = hashlib.sha512()
        m.update(str)
        return m.hexdigest()

    def login(self):
        q = ndb.gql("SELECT password, verified FROM UserModel WHERE username = :1",
                    self.username).get()
        if not q: return 0
        if (self.password == q.password):
            if q.verified:
                self.key = q.key
                return 1
            else:
                return -1
        else: return 0

class UserCookieModel(ndb.Model):
    token = ndb.StringProperty()

"""Generate a random string for cookie validation"""
def generate_cookie_token():
    return generate_random_string(50)

"""Save userid and the token for cookie validation to the cookie and database"""
def save_cookie(handler, userkey):
    token = generate_cookie_token()
    cookie_value = userkey.urlsafe() + "|" + token
    expire = datetime.now() + timedelta(days=30)
    handler.response.set_cookie("_", cookie_value, expires = expire, httponly=True, overwrite=True)
    q = ndb.Key("UserCookieModel", userkey.id()).get()
    if not q:
        model = UserCookieModel(id=userkey.id(), token=token)
        model.put()
    else:
        q.token = token
        q.put()

"""A normal lightweight class, just to be used for the return of get_current_user"""
class UserInfo:
    def __init__(self, userkey, username, email):
        self.key = ndb.Key(urlsafe=userkey)
        self.username = username
        self.email = email

"""Get the current logged in user"""
def get_current_user(handler):
    username = handler.session.get("username", None)
    if username == None:
        value = handler.request.cookies.get("_", None)
        if value == None: return None
        l = value.split("|")
        key = l[0]
        token = l[1]
        userkey = ndb.Key(urlsafe=key)
        userid = userkey.id()
        q = ndb.Key("UserCookieModel", userid).get()
        if (not q) or (q.token != token):
            return None
        else:
            q = userkey.get()
            handler.session["userkey"] = key
            handler.session["username"] = q.username
            handler.session["email"] = q.email
            return UserInfo(key, q.username, q.email)
    else:
        return UserInfo(handler.session.get("userkey"), username, handler.session.get("email"))
