from requesthandler import RequestHandler

class HomepageHandler(RequestHandler):
    def get(self):
        values = {
                "login_url": self.uri_for("login"),
                "logout_url": self.uri_for("logout"),
                "user": self.get_current_user(),
                }
        return self.render("homepage", values)
