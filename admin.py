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

class AdminTableInterface(AdminRequestHandler):
    def render_interface(self):
        pass

    def _render_interface(self, modelCls, props,
            toolbox=[],
            links=[],
            operations=[("op_delete", _("Delete selected"))],
            default_limit=20, default_order="created"):

        for prop in props:
            if not hasattr(modelCls, prop):
                raise Exception('%s does not have attribute "%s".', (modelCls.__name__, prop))
        cursor_str = self.request.get("cursor")
        cursor = Cursor(urlsafe=cursor_str) if cursor_str else Cursor()
        try:
            limit = int(self.request.get("limit", default_value=default_limit))
        except ValueError:
            limit = default_limit
        order = self.request.get("order", default_value=default_order)
        if not (order in props):
            order = default_order
        cls_order = getattr(modelCls, order)
        rcursor = cursor.reversed()
        q_forward = modelCls.query().order(cls_order)
        q_reverse = modelCls.query().order(-cls_order)
        models, next_cursor, more = q_forward.fetch_page(limit, start_cursor=cursor)
        unused_models, prev_cursor, prev_more = q_reverse.fetch_page(limit, start_cursor=rcursor)

        def get_current_url(**kwds):
            params = "?"
            params += "".join(["%s=%s" % (param[0], param[1])
                for param in {
                    "cursor": cursor.urlsafe(),
                    "limit": str(limit),
                    }
                ])
            return self.request.path + params

        values = {
                "models": models,
                "props": props,
                "toolbox": toolbox,
                "links": links,
                "operations": operations,
                "has_next": lambda: more,
                "has_prev": lambda: prev_more,
                "next_url": get_current_url(cursor=cursor),
                "prev_url": get_current_url(cursor=rcursor),
                }
        return self.render("admin_table_interface", values)

    def _get(self):
        self.render_interface()
