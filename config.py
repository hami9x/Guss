from google.appengine.ext import ndb
from google.appengine.api import memcache

def update_config_cache(name, value):
    memcache.set("config__"+name, value)

def update_config(name, value, visible):
    q = ConfigModel.query(ConfigModel.name==name).get()
    if not q:
        model = ConfigModel(name=name, value=value, visible=visible)
        model.put()
        update_config_cache(name, value)
    else:
        q.value = value
        q.visible = visible
        q.put()
        memcache.add("config__"+name, value)

def get_config(name):
    cache = memcache.get("config__"+name)
    if cache == None:
        q = ndb.gql("SELECT value FROM ConfigModel WHERE name = :1", name).get()
        if q == None:
            raise Exception("The configuration does not exist.")
        update_config_cache(name, q.value)
        return q.value
    else:
        return cache

class ConfigModel(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.StringProperty()
    visible = ndb.BooleanProperty()
