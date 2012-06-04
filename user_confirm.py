from google.appengine.api import mail
from google.appengine.ext import db
from webapp2_extras.i18n import _
import config
import utils
from user import UserModel
from requesthandler import RequestHandler

def generate_confirm_link(handler, nickname):
    token = utils.generate_random_string(30)
    link = handler.request.host_url + "/user/confirm?user=%s&token=%s" % (nickname, token)
    model = UserConfirmationModel(nickname=nickname, token=token)
    model.put()
    return link


def send_confirmation_mail(handler, nickname, email):
    mail.send_mail(sender="%s Admin <%s>" % (config.get_config("site_name"), config.get_config("admin_email")),
            to="%s <%s>" % (nickname, email),
            subject="Confirmation mail",
            body=_("""Hello %(name)s,
            Thanks for registering on our site.
            Now, click this link %(link)s to confirm your account.
            """)
                % {"name": nickname, "link": generate_confirm_link(handler, nickname)}
        )

class UserConfirmationModel(db.Model):
    nickname = db.StringProperty()
    token = db.StringProperty()

class UserConfirmHandler(RequestHandler):
    def get(self):
        nickname = self.request.get("user")
        token = self.request.get("token")
        q = db.GqlQuery("SELECT token FROM UserConfirmationModel WHERE nickname = :1", nickname).get()
        if (not q) or (q.token != token):
            values = {
                    "message": _("Your confirmation link is invalid, sorry but please check your mail box again."),
                    "redirect": None,
                    }
            self.response.out.write(self.render("noticepage", values))
        else:
            q.delete()
            the_user = UserModel.all().filter("nickname =", nickname).get()
            the_user.verified = True
            the_user.put()
            values = {
                    "message": _("Congratulations! Your account has been successfully activated \
                                    , thanks for registering."),
                    "redirect": "/",
                    }
            self.response.out.write(self.render("noticepage", values))
