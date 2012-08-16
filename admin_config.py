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
        return self.render("admin_config", values)

    def _post(self):
        q = self.get_all_visible_config()
        for conf in q:
            new_value = self.request.get(conf.name, "")
            if conf.value != new_value:
                conf.value = new_value
                conf.put()
                update_config_cache(conf.name, new_value)
        return self.redirect(self.request.headers.get("Referer", self.uri_for("admin-manage-config")))
