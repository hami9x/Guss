# Copyright 2012 Hai Thanh Nguyen
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import webapp2
from google.appengine.api import mail
from google.appengine.ext import ndb
from webapp2_extras.i18n import _
import config
import utils
from user import UserModel
from requesthandler import RequestHandler
import rbac

def generate_confirm_link(username):
    token = utils.generate_random_string(30)
    link =  webapp2.uri_for("account-confirm", _full=True)+"?user=%s&token=%s" % (username, token)
    model = UserConfirmationModel(username=username, token=token)
    model.put()
    return link


def send_confirmation_mail(username, email):
    mail.send_mail(sender="%s Admin <%s>" % (config.get_config("site_name"), config.get_config("admin_email")),
            to="%s <%s>" % (username, email),
            subject="Confirmation mail",
            body=_("""Hello %(name)s,
            Thanks for registering on our site.
            Now, click this link %(link)s to confirm your account.
            """)
                % {"name": username, "link": generate_confirm_link(username)}
        )

class UserConfirmationModel(ndb.Model):
    username = ndb.StringProperty()
    token = ndb.StringProperty()

class UserConfirmHandler(RequestHandler):
    def get(self):
        username = self.request.get("user")
        token = self.request.get("token")
        q = ndb.gql("SELECT token FROM UserConfirmationModel WHERE username = :1", username).get()
        if (not q) or (q.token != token):
            values = {
                    "message": _("Your confirmation link is invalid, sorry but please check your mail box again."),
                    "redirect": None,
                    }
            return self.render("noticepage", values)
        else:
            q.delete()
            the_user = UserModel.query(UserModel.username==username).get()
            the_user.verified = True
            user_key = the_user.put()
            rbac.add_role(user_key, rbac.default_role("registered"))
            values = {
                    "message": _("Congratulations! Your account has been successfully activated \
                                    , thanks for registering."),
                    "redirect": self.uri_for("home"),
                    }
            return self.render("noticepage", values)
