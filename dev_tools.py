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

from random import choice
import datetime
from google.appengine.ext import ndb
import forum, utils, user
from requesthandler import RequestHandler

def class_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

class ModelGenerator(RequestHandler):
    def _check_permission(self):
        return self.current_user_check_permission("root")

    def get_n(self):
        times = self.request.get("n")
        try: times = int(times)
        except ValueError:
            times = 1
        return times


    def _get(self):
        importStr = self.request.get("class")
        times = self.get_n()
        prop_values = {}
        data = self.request.GET.dict_of_lists()
        for k, l in data.iteritems():
            if k.startswith("prop_"):
                v = l[0]
                prop = k[5:]
                prop_values[prop] = v


        cls = class_import(importStr)
        types = [
            (ndb.IntegerProperty, lambda: choice([i for i in range(0, 9)])),
            (ndb.StringProperty, lambda: utils.generate_random_string(8)),
            (ndb.BooleanProperty, lambda: choice([True, False])),
            (ndb.DateTimeProperty, lambda: datetime.datetime.now()),
            ]
        for unused_i in range(times):
            model = cls()
            for prop, val in model._properties.items():
                for t in types:
                    if isinstance(val, t[0]):
                        setattr(model, prop, t[1]())
                        break
                if prop in prop_values:
                    setattr(model, prop, prop_values[prop])
            model.put(force_validation=False)
        self.response.out.write("OK")

class ForumReplyGenerator(ModelGenerator):
    def _get(self):
        parent = int(self.request.get("parent"))
        master = forum.ThreadModel.get_by_id(parent)
        for i in range(0, self.get_n()):
            forum.ReplyModel(parent=master.key,
                    content=utils.generate_random_string(50),
                    author=user.UserModel.query().get().key) \
                .put(master=master, pagination=master.default_pagination())
        self.response.out.write("OK")
