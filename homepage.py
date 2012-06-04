from requesthandler import RequestHandler
import user_auth

class HomepageHandler(RequestHandler):
    def get(self):
        values = {
                "login_url": user_auth.get_login_url(),
                "logout_url": user_auth.get_logout_url(),
                "user": self.get_current_user(),
                }
        self.response.out.write(self.render("homepage", values))
