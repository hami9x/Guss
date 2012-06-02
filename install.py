from requesthandler import RequestHandler
import user

class InstallHandler(RequestHandler):
    def get(self):
        q = user.UserModel.all().filter("nickname =", "admin").get()
        if not q:
            model = user.UserModel(nickname="admin", password="admin", email="admin@gmail.com", verified=True)
            model.put()

        self.response.out.write("<html><body>Install successful.</body></html>")

