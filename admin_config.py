from google.appengine.ext import db
from requesthandler import RequestHandler
from config import update_config_cache

class AdminConfigHandler(RequestHandler):
    def get_all_visible_config(self):
        return db.GqlQuery("SELECT * FROM ConfigModel WHERE visible = TRUE ORDER BY name")

    def get(self):
        q = self.get_all_visible_config()
        values = {
                "configs": q
                }
        self.response.out.write(self.render("admin_config", values))

    def post(self):
        q = self.get_all_visible_config()
        for conf in q:
            new_value = self.request.get(conf.name, "")
            if conf.value != new_value:
                conf.value = new_value
                conf.put()
                update_config_cache(conf.name, new_value)
        return self.redirect(self.request.headers.get("Referer", self.uri_for("manage-config")))
