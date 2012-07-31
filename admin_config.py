from config import update_config_cache, ConfigModel
import admin

class AdminConfigHandler(admin.AdminRequestHandler):
    def _check_permission(self):
        return self.current_user_check_permission("config")

    def get_all_visible_config(self):
        return ConfigModel.query(ConfigModel.visible==True).order(ConfigModel.name)

    def _get(self):
        q = self.get_all_visible_config()
        values = {
                "configs": q
                }
        self.response.out.write(self.render("admin_config", values))

    def _post(self):
        q = self.get_all_visible_config()
        for conf in q:
            new_value = self.request.get(conf.name, "")
            if conf.value != new_value:
                conf.value = new_value
                conf.put()
                update_config_cache(conf.name, new_value)
        return self.redirect(self.request.headers.get("Referer", self.uri_for("manage-config")))
