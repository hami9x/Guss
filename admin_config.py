from google.appengine.ext import db
from requesthandler import RequestHandler

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
        for config in q:
            new_value = self.request.get(config.name, "")
            if config.value != new_value:
                config.value = new_value
                config.put()
        return self.redirect(self.request.headers.get("Referer", "/admin/config"))
