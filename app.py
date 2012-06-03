import webapp2
import install
import homepage
import authhandler
import admin_user

tempconfig = {}
tempconfig["webapp2_extras.sessions"] = {
            "secret_key": "temporary_secret_key",
            }

app = webapp2.WSGIApplication([
                                (authhandler.get_login_url(), authhandler.LoginHandler),
                                (authhandler.get_logout_url(), authhandler.LogoutHandler),
                                ("/install", install.InstallHandler),
                                ("/admin/user/add", admin_user.AdminAddUserHandler),
                                ("/admin/user", admin_user.AdminUserHandler),
                                ("/", homepage.HomepageHandler),
                            ], debug=True, config=tempconfig)
