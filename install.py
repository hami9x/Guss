import webapp2
from user import UserModel
import utils
import config

class InstallHandler(webapp2.RequestHandler):
    def get(self):
        q = UserModel.all().filter("nickname =", "admin").get()
        if not q:
            model = UserModel(nickname="admin", password="admin", email="admin@gmail.com", verified=True)
            model.put()

        conf = [
                ("site_name", "Name", True),
                ("session_secret_key", utils.generate_random_string(30), False),
                ("admin_email", "admin@gmail.com", True)
            ]
        for item in conf:
            config.update_config(item[0], item[1], item[2])

        self.response.out.write("<html><body>Install successful.</body></html>")

app = webapp2.WSGIApplication([("/install", InstallHandler)], debug=True)
