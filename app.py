import webapp2
import config

tempconfig = {}
tempconfig["webapp2_extras.sessions"] = {
            "secret_key": config.get_config("session_secret_key").encode("ascii", "ignore")
            }

app = webapp2.WSGIApplication([
                    webapp2.Route("/user/login", handler="user_auth.LoginHandler", name="login"),
                    webapp2.Route("/user/logout", handler="user_auth.LogoutHandler", name="logout"),
                    webapp2.Route("/user/confirm", handler="user_confirm.UserConfirmHandler", name="account-confirm"),
                    webapp2.Route("/admin/config", handler="admin_config.AdminConfigHandler", name="manage-config"),
                    webapp2.Route("/admin/user/add", handler="admin_user.AdminAddUserHandler", name="admin-add-user"),
                    webapp2.Route("/admin/user", handler="admin_user.AdminUserHandler", name="manage-user"),
                    webapp2.Route(r"/admin/user/edit/<keystr:[\w-]*>", handler="admin_user.AdminEditUserHandler", name="admin-edit-user"),
                    webapp2.Route(r"/blog/edit/<slug:[\w-]*>", handler="blog_edit.BlogEditHandler", name="blog-edit"),
                    webapp2.Route(r"/blog/view/<slug:[\w-]*>", handler="blog_view.BlogViewHandler", name="blog-view"),
                    webapp2.Route("/", handler="homepage.HomepageHandler", name="home"),
                ], debug=True, config=tempconfig)
