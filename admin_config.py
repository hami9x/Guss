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
from google.appengine.ext import ndb
import admin, model

class FakeModel(model.FormModel):
    pass

class AdminConfigHandler(admin.AdminEditInterface):
    def _check_permission(self):
        return self.current_user_check_permission("config")

    def get_all_visible_config(self):
        return ConfigModel.query(ConfigModel.visible==True).order(ConfigModel.name)

    def _handler_init_after_permission(self):
        q = self.get_all_visible_config()
        fake_mclass = FakeModel
        validators = {}
        iterlist = []
        for conf in q:
            ty = type(conf.value)
            if ty == int:
                prop_type = model.IntegerProperty
                validators[conf.name] = {"integer": ()}
            elif ty == bool:
                prop_type = model.BooleanProperty
            else:
                prop_type = ndb.StringProperty
            setattr(fake_mclass, conf.name, prop_type())
            get_val = self.request.get(conf.name)
            if get_val: conf.value = get_val
            iterlist.append(conf)

        self.model = model.MyMetaModel(fake_mclass.__name__, fake_mclass.__bases__, dict(fake_mclass.__dict__))()
        import logging; logging.info(self.model.__class__.__name__)
        self.model._validation = lambda: validators
        for conf in iterlist:
            setattr(self.model, conf.name, conf.value)
        self._all_config = iterlist

    def _post(self):
        if self.model.validate():
            for conf in self._all_config:
                conf.value = getattr(self.model, conf.name)
                conf.put()
                update_config_cache(conf.name, conf.value)
        self.render_interface(self.model)
