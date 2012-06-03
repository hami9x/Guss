from requesthandler import RequestHandler
import user
import utils

class InstallHandler(RequestHandler):
    def get(self):
        q = user.UserModel.all().filter("nickname =", "admin").get()
        if not q:
            model = user.UserModel(nickname="admin", password="admin", email="admin@gmail.com", verified=True)
            model.put()

        config = [
                ("session_secret_key", utils.generate_random_string(30), False),
                ("admin_email", "admin@gmail.com", True)
            ]
        for item in config:
            self.update_config(item[0], item[1], item[2])

        self.response.out.write("<html><body>Install successful.</body></html>")

