import webapp2
import homepage
import authhandler
import admin_user
import admin_config
import config

tempconfig = {}
tempconfig["webapp2_extras.sessions"] = {
            "secret_key": config.get_config("session_secret_key")
            }

app = webapp2.WSGIApplication([
                                (authhandler.get_login_url(), authhandler.LoginHandler),
                                (authhandler.get_logout_url(), authhandler.LogoutHandler),
                                ("/admin/config", admin_config.AdminConfigHandler),
                                ("/admin/user/add", admin_user.AdminAddUserHandler),
                                ("/admin/user", admin_user.AdminUserHandler),
                                ("/", homepage.HomepageHandler),
                            ], debug=True, config=tempconfig)
