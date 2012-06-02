import webapp2
import install
import homepage
import authhandler

tempconfig = {}
tempconfig["webapp2_extras.sessions"] = {
            "secret_key": "temporary_secret_key",
            }

app = webapp2.WSGIApplication([
                                (authhandler.get_login_url(), authhandler.LoginHandler),
                                (authhandler.get_logout_url(), authhandler.LogoutHandler),
                                ("/install", install.InstallHandler),
                                ("/", homepage.HomepageHandler),
                            ], debug=True, config=tempconfig)
