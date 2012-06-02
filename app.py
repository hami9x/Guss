import webapp2
import user
import install

tempconfig = {}
tempconfig["webapp2_extras.sessions"] = {
            "secret_key": "temporary_secret_key",
            }

app = webapp2.WSGIApplication([
                                ("/user/login", user.LoginHandler),
                                ("/install", install.InstallHandler),
                            ], debug=True, config=tempconfig)
