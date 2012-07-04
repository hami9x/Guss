"""Role-Based Access Control system

    Implements the hierarchical model of role-based access control.
"""

from google.appengine.ext import ndb

class RoleModel(ndb.Model):
    parents = ndb.KeyProperty(repeated=True)
    name = ndb.StringProperty()

class PermissionModel(ndb.Model):
    desc = ndb.StringProperty()

class RoleAssignmentModel(ndb.Model):
    user_key = ndb.KeyProperty()
    role_key = ndb.KeyProperty()

class PermissionAssignmentModel(ndb.Model):
    role_key = ndb.KeyProperty()
    perm_id = ndb.StringProperty()

def register_permission(perm_id, desc):
    """Create a new permission
    NOTICE: Permission registrations (using this function) MUST be put in the register_permissions function of permissions.py
        You must go to /upgrade for this function to take effect
    """
    q = PermissionModel.get_by_id(perm_id)
    if not q:
        model = PermissionModel(id=perm_id, desc=desc)
        model.put()

def register_role(name, parents=[]):
    """Create a new role
    Args:
      name: A human-readable name for the role
      parents: A list of keys of the roles to be used as this role's parent
    """
    #Make sure that the parents are all valid
    for parent_key in parents:
        if parent_key.get() == None:
            raise Exception(u'The parent role with id "%s" does not exist.' % parent_key.id())
    return RoleModel(name=name, parents=parents).put()

def add_role(user_key, role_key):
    """Assign a new role to a user"""
    q = RoleAssignmentModel.gql("WHERE user_key = :1 AND role_key = :2", user_key, role_key)
    if q.count(1) == 0:
        model = RoleAssignmentModel(user_key=user_key, role_key=role_key)
        model.put()

def has_permission(role_key, perm_id):
    q = PermissionAssignmentModel.gql("WHERE role_key = :1 AND perm_id = :2", role_key, perm_id)
    return q.count(1) > 0

def check_permission_role(role_key, perm_id):
    """Check if a role is allowed to do something"""
    if has_permission(role_key, perm_id):
        return True
    else:
        parents = role_key.get().parents
        for parent in parents:
            if check_permission_role(parent, perm_id):
                return True
        return False

def allow(role_key, perm_id):
    """Assign a permission to a role"""
    if not has_permission(role_key, perm_id):
        model = PermissionAssignmentModel(role_key=role_key, perm_id=perm_id)
        model.put()

def get_roles(user_key):
    q = ndb.gql("SELECT role_key FROM RoleAssignmentModel WHERE user_key = :1", user_key)
    return [role.role_key for role in q]

def check_permission(user_key, perm_id):
    """Check if a user is allowed to do something"""
    if PermissionModel.get_by_id(perm_id) == None:
        raise Exception(u'Permission "%s" does not exist' % perm_id)
    roles = get_roles(user_key)
    for role_key in roles:
        if check_permission_role(role_key, perm_id):
            return True
    return False
