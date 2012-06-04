from google.appengine.ext import db
from google.appengine.api import memcache

def update_config_cache(name, value):
    memcache.set("config__"+name, value)

def update_config(name, value, visible):
    q = db.GqlQuery("SELECT * FROM ConfigModel WHERE name = :1", name).get()
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
        q = db.GqlQuery("SELECT value FROM ConfigModel WHERE name = :1", name).get()
        update_config_cache(name, q.value)
        return q.value
    else:
        return cache

class ConfigModel(db.Model):
    name = db.StringProperty()
    value = db.StringProperty()
    visible = db.BooleanProperty()

