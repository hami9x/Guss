from requesthandler import RequestHandler
import user

class HomepageHandler(RequestHandler):
    def get(self):
        values = {
                "login_url": user.get_login_url(),
                "user": self.get_current_user(),
                }
        self.response.out.write(self.render("homepage", values))
