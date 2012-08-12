from google.appengine.ext import ndb
from requesthandler import RequestHandler
from random import choice
import utils
import datetime

def class_import(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

class ModelGenerator(RequestHandler):
    def _check_permission(self):
        return self.current_user_check_permission("root")

    def _get(self):
        importStr = self.request.get("class")
        times = self.request.get("n")
        try: times = int(times)
        except ValueError:
            times = 1

        cls = class_import(importStr)
        types = [
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
            model.put(force_validation=False)
        self.response.out.write("OK")
