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

from google.appengine.datastore.datastore_query import Cursor
from webapp2_extras.i18n import _
from requesthandler import RequestHandler
import webapp2


class AdminRequestHandler(RequestHandler):
    def _check_permission(self):
        return self.current_user_check_permission("access_acp")

class AdminEditInterface(AdminRequestHandler):
    def render_interface(self, model):
        self._render_interface(model)

    def _render_interface(self, model, exclude_props=[], options={}):
        model_dict = model.to_dict(exclude=exclude_props)

        self.render("admin_edit_interface", {
            "props": model_dict,
            "model": model,
            "options": options,
            })

    def _get(self, *args, **kwds):
        self.render_interface(self.model)

    def _post(self, *args, **kwds):
        self.model.assign(self)
        self._put_and_render()

    def _put_and_render(self):
        if self.model.validate():
            self.model.put()
        self.render_interface(self.model)

class UriForTool(object):
    def __init__(self, uri_name, **kwds):
        self._uri_name = uri_name
        self._params = kwds

    def get_uri(self, model):
        params = {}
        for k, attr_tuple in self._params.items():
            attr = attr_tuple[0]
            try:
                fn = attr_tuple[1] #get the attribute manipulation function
                params[k] = fn(getattr(model, attr))
            except IndexError:
                params[k] = getattr(model, attr)
        return webapp2.uri_for(self._uri_name, **params)

NOTHING = object()
class AdminTableOptions(object):
    def __init__(self, model_cls, props,
            toolbox=[],
            links=[],
            operations=NOTHING,
            default_limit=20, default_order="created"):
        if operations is NOTHING:
            operations=[("op_delete", _("Delete selected"), lambda model: model.key.delete())]
        for prop in props:
            if not hasattr(model_cls, prop):
                raise Exception('%s does not have attribute "%s".', (model_cls.__name__, prop))
        for param, val in locals().items():
            setattr(self, param, val)

class AdminTableInterface(AdminRequestHandler):
    def __init__(self, *args, **kwds):
        super(AdminTableInterface, self).__init__(*args, **kwds)
        self._options = self.table_options()

    def _table_options(self, *args, **kwds):
        return AdminTableOptions(*args, **kwds)

    def table_options(self):
        pass

    def option(self, name):
        return getattr(self._options, name)

    def render_interface(self, **kwds):
        default_limit = self.option("default_limit")
        default_order = self.option("default_order")
        model_cls = self.option("model_cls")
        props = self.option("props")
        cursor_str = self.request.get("cursor")
        cursor = Cursor(urlsafe=cursor_str) if cursor_str else Cursor()
        try:
            limit = int(self.request.get("limit", default_value=default_limit))
        except ValueError:
            limit = default_limit
        order = self.request.get("order", default_value=default_order)
        if not (order in props):
            order = default_order
        cls_order = getattr(model_cls, order)
        rcursor = cursor.reversed()
        q_forward = model_cls.query().order(cls_order)
        q_reverse = model_cls.query().order(-cls_order)
        models, next_cursor, more = q_forward.fetch_page(limit, start_cursor=cursor)
        unused_models, prev_cursor, unused_prev_more = q_reverse.fetch_page(limit, start_cursor=rcursor)

        def get_current_url(cursor, **kwds):
            params = "?"
            params += "&".join(["%s=%s" % (k, v)
                for k, v in {
                    "cursor": cursor.urlsafe(),
                    "limit": str(limit),
                    }.iteritems()
                ])
            return self.request.path + params

        values = {
                "models": models,
                "props": props,
                "toolbox": self.option("toolbox"),
                "links": self.option("links"),
                "operations": self.option("operations"),
                "has_next": lambda: more,
                "has_prev": lambda: (cursor != Cursor()) and (prev_cursor != None),
                "next_url": get_current_url(cursor=next_cursor),
                "prev_url": get_current_url(cursor=prev_cursor.reversed()) if prev_cursor else "",
                }
        return self.render("admin_table_interface", values)


    def _get(self):
        self.render_interface()

    def _post(self):
        model_cls = self.option("model_cls")
        selected = self.request.get("checklist", allow_multiple=True)
        for model_id in selected:
            model = model_cls.get_by_id(int(model_id))
            if model is None:
                raise Exception("the model ID submitted is invalid.")
            for operation in self.option("operations"):
                fn = operation[2]
                fn(model)
        self.render_interface()
