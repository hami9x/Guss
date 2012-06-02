from requesthandler import RequestHandler
import authhandler

class HomepageHandler(RequestHandler):
    def get(self):
        values = {
                "login_url": authhandler.get_login_url(),
                "logout_url": authhandler.get_logout_url(),
                "user": self.get_current_user(),
                }
        self.response.out.write(self.render("homepage", values))
