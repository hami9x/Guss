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

from webapp2_extras.i18n import _

import rbac
def register_permissions():
    permissions = [
                ("root", _(u"The right to modify most dangerous things, only given to the root user")),
                ("access_acp", _(u"Access the Admin Control Panel")),
                ("manage_user", _(u"Manage users")),
                ("config", _(u"Edit important site configurations.")),
                ("edit_own_post", _(u"Edit user's own posts.")),
                ("edit_all_post", _(u"Edit posts of any users.")),
                ("view_post", _(u"View user posts.")),
                ("manage_post", _(u"Manage user posts.")),
                ]

    for item in permissions:
        rbac.register_permission(*item)

def install_rbac_default():
    rbac.default_role("super_admin", _(u"Super Admin"))
    guest = rbac.default_role("guest", _(u"Guest"))
    registered = rbac.default_role("registered", _(u"Registered User"), parents=[guest])
    admin = rbac.default_role("admin", _(u"Admin"), parents=[registered])
    rbac.allow(guest, ["view_post"])
    rbac.allow(registered, ["edit_own_post"])
    rbac.allow(admin, ["access_acp", "manage_user", "manage_post"])
