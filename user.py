import webapp2
from google.appengine.ext import db
import common

class UserModel:
    nickname = db.StringProperty()
    password = db.StringProperty()
    email = db.EmailProperty()
    verified = db.BooleanProperty()

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(common.render_template("loginpage"))
