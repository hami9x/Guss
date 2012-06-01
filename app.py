import webapp2
import user

app = webapp2.WSGIApplication([
                                ("/user/login", user.LoginHandler)
                            ], debug=True)
