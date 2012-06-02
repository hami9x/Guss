import webapp2
import user
import install

app = webapp2.WSGIApplication([
                                ("/user/login", user.LoginHandler),
                                ("/install", install.InstallHandler),
                            ], debug=True)
