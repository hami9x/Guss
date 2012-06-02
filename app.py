import webapp2
import user
import install
import homepage

tempconfig = {}
tempconfig["webapp2_extras.sessions"] = {
            "secret_key": "temporary_secret_key",
            }

app = webapp2.WSGIApplication([
                                ("/user/login", user.LoginHandler),
                                ("/install", install.InstallHandler),
                                ("/", homepage.HomepageHandler),
                            ], debug=True, config=tempconfig)
