from webapp2_extras.i18n import _

import rbac
def register_permissions():
    permissions = [
                ("access_acp", _(u"Access the Admin Control Panel")),
                ("manage_user", _(u"Manage users")),
                ("config", _(u"Edit important site configurations.")),
                ]

    for item in permissions:
        rbac.register_permission(*item)

def install_rbac_default():
    rbac.default_role("super_admin", _(u"Super Admin"))
    rbac.default_role("guest", _(u"Guest"))
    rbac.default_role("registered_user", _(u"Registered User"))
    rbac.default_role("unverified_user", _(u"Unverified User"))
    admin = rbac.default_role("admin", _(u"Admin"))
    rbac.allow(admin, ["access_acp", "manage_user"])
