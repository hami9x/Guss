import webapp2
import homepage
import user_auth
import user_confirm
import admin_user
import admin_config
import config

tempconfig = {}
tempconfig["webapp2_extras.sessions"] = {
            "secret_key": config.get_config("session_secret_key")
            }

app = webapp2.WSGIApplication([
                                (user_auth.get_login_url(), user_auth.LoginHandler),
                                (user_auth.get_logout_url(), user_auth.LogoutHandler),
                                ("/user/confirm", user_confirm.UserConfirmHandler),
                                ("/admin/config", admin_config.AdminConfigHandler),
                                ("/admin/user/add", admin_user.AdminAddUserHandler),
                                ("/admin/user", admin_user.AdminUserHandler),
                                ("/", homepage.HomepageHandler),
                            ], debug=True, config=tempconfig)
