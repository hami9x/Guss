from webapp2_extras.i18n import _
from requesthandler import RequestHandler
import user

class LoginHandler(RequestHandler):
    def get(self):
        render_notice = lambda values: self.render("noticepage", values)

        successful = self.request.get("successful", None)
        if successful == "1":
            values = {
                    "message": _("You successfully signed in, welcome back!"),
                    "redirect": self.request.get("referer"),
                    }
            return render_notice(values)
        elif successful == "0":
            values = {
                    "message": _("Login failed, invalid password or user doesn't exist, you could try again."),
                    "redirect": self.uri_for("login"),
                    }
            return render_notice(values)
        elif successful == "-1":
            values = {
                    "message": _("The user is valid but not verified,\
                            check your email to find the confirmation link\
                            we sent to you when you registered."),
                    "redirect": None,
                    }
            return render_notice(values)
        else:
            if self.get_current_user() != None:
                values = {
                        "message": _("You've logged in, why do you want to do this again?"),
                        "redirect": self.uri_for("home"),
                        }
                return render_notice(values)
            else:
                values = { "referer": self.request.headers.get("Referer", self.uri_for("home")) }
                self.render("loginpage", values)

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        referer = self.request.get("referer")
        model = user.UserModel(username=username, password=password)
        login = model.login()
        if login == 1:
            user.save_cookie(self, model.key)
        return self.redirect(self.uri_for("login")+"?successful=%s&referer=%s" % (str(login), referer))

class LogoutHandler(RequestHandler):
    def get(self):
        self.response.delete_cookie("_")
        self.session["username"] = None
        return self.redirect(self.uri_for("home"))
