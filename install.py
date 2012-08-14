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
from user import UserModel
import utils
import config
import rbac
import rbac_setup

def install_rbac():
    rbac_setup.register_permissions()
    rbac_setup.install_rbac_default()

def perform_installation(*args, **kwds):
    #Set up Role-based Access Control
    install_rbac();

    q = UserModel.query(UserModel.username=="admin").get()
    if not q:
        model = UserModel(username="admin", password="admin", email="admin@gmail.com", verified=True)
        model.put(force_validation=False)
        rbac.add_role(model.key, rbac.default_role("super_admin"))

    #Configurations
    conf = [
            ("site_name", "Name", True),
            ("session_secret_key", utils.generate_random_string(30), False),
            ("admin_email", "admin@gmail.com", True),
            ("user_email_confirm", "no", True),
        ]
    for item in conf:
        config.update_config(item[0], item[1], item[2])

class InstallHandler(webapp2.RequestHandler):
    def get(self):
        perform_installation();
        self.response.out.write("<html><body>Install successful.</body></html>")


app = webapp2.WSGIApplication([("/install", InstallHandler)], debug=True)
