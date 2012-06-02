from webapp2_extras.i18n import _
from requesthandler import RequestHandler
import user

def get_login_url():
    return "/user/login"

def get_logout_url():
    return "/user/logout"


class LoginHandler(RequestHandler):
    def get(self):
        render_notice = lambda values: self.response.out.write(self.render("noticepage", values))

        successful = self.request.get("successful", None)
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
            if self.get_current_user() != None:
                values = {
                        "message": _("You've logged in, why do you want to do this again?"),
                        "redirect": "/",
                        }
                render_notice(values)
            else:
                values = { "referer": self.request.headers.get("Referer", "/") }
                self.response.out.write(self.render("loginpage", values))

    def post(self):
        nickname = self.request.get("nickname")
        password = self.request.get("password")
        referer = self.request.get("referer")
        model = user.UserModel(nickname=nickname, password=password)
        login = model.login()
        if login == 1:
            user.save_cookie(self, nickname)
        return self.redirect(get_login_url()+"?successful=%s&referer=%s" % (str(login), referer))

class LogoutHandler(RequestHandler):
    def get(self):
        self.response.delete_cookie("_")
        self.session["nickname"] = None
        return self.redirect("/")
