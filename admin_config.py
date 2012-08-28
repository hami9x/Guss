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

import admin, model, config, config_setup

class FakeModel(model.FormModel):
    pass

class AdminConfigHandler(admin.AdminEditInterface):
    def _check_permission(self):
        return self.current_user_check_permission("config")

    def get_all_visible_config(self):
        return config.ConfigModel.query(config.ConfigModel.visible==True).order(config.ConfigModel.name)

    def _handler_init_after_permission(self):
        self.configs_db = self.get_all_visible_config()
        configs = config_setup.default_configs()
        fake_mclass = FakeModel
        validators = {}
        for conf in configs:
            if conf.visible:
                validators[conf.name] = conf.validation()
                setattr(fake_mclass, conf.name, conf.prop_class())

        fake_mclass._validation = lambda obj: validators
        self.model = model.MyMetaModel(fake_mclass.__name__, fake_mclass.__bases__, dict(fake_mclass.__dict__))()
        for conf in self.configs_db:
            setattr(self.model, conf.name, self.request.get(conf.name) or conf.value)

    def _post(self):
        if self.model.validate():
            for conf in self.configs_db:
                conf.value = getattr(self.model, conf.name)
                conf.put()
                config.update_config_cache(conf.name, conf.value)
        self.render_interface(self.model)
