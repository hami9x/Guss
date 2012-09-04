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

from webapp2_extras.i18n import _
from requesthandler import RequestHandler
import webapp2
import utils


class AdminRequestHandler(RequestHandler):
    def _check_permission(self):
        return self.current_user_check_permission("access_acp")

class AdminEditInterface(AdminRequestHandler):
    def render_interface(self, model):
        """To be overridden by a subclass to _render_interface with some customizations."""
        self._render_interface(model)

    def _render_interface(self, model, exclude_props=[], options={}):
        """Render the interface with specific parameters.
        Sshould only be used in a method that overrides render_interface.
        Args:
            model: the entity to be edited
            exclude_props: properties that shouldn't be edited
            options: options regarding the properties
        """
        model_dict = model.to_dict(exclude=exclude_props)

        self.render("admin_edit_interface", {
            "props": model_dict,
            "model": model,
            "options": options,
            })

    def _get(self, *args, **kwds):
        """Shouldn't be overridden."""
        self.render_interface(self.model)

    def _post(self, *args, **kwds):
        """Should only override it when absolutely necessary."""
        self.model.assign(self)
        self._put_and_render()

    def _put_and_render(self):
        if self.model.validate():
            self.model.put()
        self.render_interface(self.model)

class UriForTool(object):
    """Represents a "tool" link for each item in the table interface.
    This is a class that helps customizing the behavior of the table interface (see AdminTableInterface class.
    Each link (for example, an Edit link) usually requires some info from each entity, so adding those links
    in the table wouldn't be possileb without this class.
    Consider this a special version of uri_for().
    """
    def __init__(self, uri_name, **kwds):
        self._uri_name = uri_name
        self._params = kwds

    """Get the link."""
    def get_uri(self, model):
        params = {}
        for k, attr in self._params.items():
            if isinstance(attr, tuple):
                attr_name = attr[0]
                fn = attr[1] #get the attribute manipulation function
                params[k] = fn(getattr(model, attr_name))
            else:
                params[k] = getattr(model, attr)
        return webapp2.uri_for(self._uri_name, **params)

NOTHING = object()
class AdminTableOptions(object):
    def __init__(self, model_cls, props,
            toolbox=[],
            links=[],
            operations=NOTHING,
            default_limit=20, default_order="created"):
        """Specify interface options for the table.
        Args:
            model_cls: the Model class, items listed in this table are this model's entities
            props: list of properties to be used as columns of the table
            toolbox: list of links for each row in the table, for example, Edit
            operations: list of bulk actions that could be done, for example, Delete Seleted
            default_limit: the default number of items to be shown
            default_order: the default order for the items
        """
        if operations is NOTHING:
            operations=[("op_delete", _("Delete selected"), lambda model: model.key.delete())]
        for param, val in locals().items():
            setattr(self, param, val)

class AdminTableInterface(AdminRequestHandler):
    def __init__(self, *args, **kwds):
        super(AdminTableInterface, self).__init__(*args, **kwds)
        self._options = self.table_options()

    def _table_options(self, *args, **kwds):
        """To be used in table_options() for specifying the table options.
        See the AdminTableOptions class for some clues about the options available and
        look at the code of this class's subclasses for usage examples."""
        return AdminTableOptions(*args, **kwds)

    def table_options(self):
        """Must be overridden by a child class, this method should use _table_options() to specify the options."""
        pass

    def option(self, name):
        """Get value of an option."""
        return getattr(self._options, name)

    def render_interface(self, **kwds):
        """Render the inteface."""
        default_limit = self.option("default_limit")
        default_order = self.option("default_order")
        props = self.option("props")
        try:
            limit = int(self.request.get("limit", default_value=default_limit))
        except ValueError:
            limit = default_limit
        order = self.request.get("order", default_value=default_order)
        if not (order in props):
            order = default_order

        pagin = utils.NextPrevPagination(model_cls=self.option("model_cls"),
                order=order,
                limit=limit,
                cursor_str = self.request.get("cursor"),
                );

        def table_model_attr(model, attr):
            """Help showing content of the columns."""
            if attr.endswith("()"):
                return getattr(model, attr[:-2])()
            else: return getattr(model, attr)

        values = {
                "table_model_attr": table_model_attr,
                "models": pagin.items(),
                "props": props,
                "toolbox": self.option("toolbox"),
                "links": self.option("links"),
                "operations": self.option("operations"),
                "pagin": pagin,
                }
        return self.render("admin_table_interface", values)


    def _get(self):
        """Shouldn't be overridden."""
        self.render_interface()

    def _post(self):
        """Shouldn't be overridden."""
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
