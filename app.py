# Copyright 2012 Hai Thanh Nguyen
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
                    webapp2.Route("/admin/config", handler="admin_config.AdminConfigHandler", name="admin-manage-config"),
                    webapp2.Route("/admin/user/add", handler="admin_user.AdminAddUserHandler", name="admin-add-user"),
                    webapp2.Route("/admin/user", handler="admin_user.AdminUserHandler", name="admin-manage-user"),
                    webapp2.Route(r"/admin/user/edit/<keystr:[\w-]*>", handler="admin_user.AdminEditUserHandler", name="admin-edit-user"),
                    webapp2.Route(r"/blog/edit/<slug:[\w-]*>", handler="blog_edit.BlogEditHandler", name="blog-edit"),
                    webapp2.Route(r"/blog/view/<slug:[\w-]*>", handler="blog_view.BlogViewHandler", name="blog-view"),
                    webapp2.Route("/admin/dev/generate", handler="dev_tools.ModelGenerator", name="dev-generate"),
                    webapp2.Route("/", handler="homepage.HomepageHandler", name="home"),
                ], debug=True, config=tempconfig)
