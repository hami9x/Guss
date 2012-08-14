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

from google.appengine.ext import ndb
from webapp2_extras.i18n import _
from user import UserModel
from google.net.proto import ProtocolBuffer
import user_confirm
import admin
import config
import rbac

def can_manage_user(handler):
    return handler.current_user_check_permission("manage_user")

#User management page
class AdminUserHandler(admin.AdminTableInterface):
    def _check_permission(self): return can_manage_user(self)

    def table_options(self):
        fn_urlsafe = lambda key: key.urlsafe()
        return self._table_options(UserModel, props=["username", "email", "created", "verified"],
                toolbox=[(_("Edit"), admin.UriForTool("admin-edit-user", keystr=("key", fn_urlsafe)))],
                links=[(_("Add"), self.uri_for("admin-add-user"))]
        )

    def model_class(self):
        return UserModel

class AdminAddUserHandler(admin.AdminRequestHandler):
    def _check_permission(self): return can_manage_user(self)

    def _get(self):
        model = UserModel()
        return self.render("admin_user_add", {"model": model})

    def _post(self):
        username = self.request.get("username")
        email = self.request.get("email")
        model = UserModel(verified=False)
        model.assign(self)
        if model.validate():
            if config.get_config("user_email_confirm") == "yes":
                model.put()
                user_confirm.send_confirmation_mail(username, email)
                values = {
                        "message": _(u"""An email that contains the link to activate the account \
                            has been sent to the email"""),
                        "redirect": None,
                        }
                return self.render("noticepage", values)
            else:
                model.verified = True
                user_key = model.put()
                rbac.add_role(user_key, rbac.default_role("registered"))
                values = {
                        "message": _(u"""Successfully registered."""),
                        "redirect": None,
                        }
                return self.render("noticepage", values)
        else:
            values = {
                    "model": model
                    }
            return self.render("admin_user_add", values)

class AdminEditUserHandler(admin.AdminEditInterface):
    def _check_permission(self): return can_manage_user(self)

    def render_interface(self, model):
        model.password = ""
        self._render_interface(model, exclude_props=["created"], options={
        "password_confirm": {
            "input_type": "password",
            },
        })

    def _handler_init(self, keystr=""):
        try:
            self.model = ndb.Key(urlsafe=keystr).get()
        except ProtocolBuffer.ProtocolBufferDecodeError:
            self.render("noticepage", {
                "message": _("User key is not valid."),
                })

    def _post(self, *args, **kwds):
        orig_password = self.model.password
        self.model.assign(self)
        if self.request.get("password") == "":
            self.model.password = orig_password
        self._put_and_render()
