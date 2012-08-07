from webapp2_extras.i18n import _

import rbac
def register_permissions():
    permissions = [
                ("access_acp", _(u"Access the Admin Control Panel")),
                ("manage_user", _(u"Manage users")),
                ("config", _(u"Edit important site configurations.")),
                ("edit_own_blog", _(u"Edit user's own blogs.")),
                ("edit_all_blog", _(u"Edit blogs of any users.")),
                ]

    for item in permissions:
        rbac.register_permission(*item)

def install_rbac_default():
    rbac.default_role("super_admin", _(u"Super Admin"))
    guest = rbac.default_role("guest", _(u"Guest"))
    registered = rbac.default_role("registered", _(u"Registered User"), parents=[guest])
    admin = rbac.default_role("admin", _(u"Admin"), parents=[registered])
    rbac.allow(registered, ["edit_own_blog"])
    rbac.allow(admin, ["access_acp", "manage_user"])
