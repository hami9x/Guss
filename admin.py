from requesthandler import RequestHandler

class AdminRequestHandler(RequestHandler):
    def _check_permission(self):
        return self.current_user_check_permission("access_acp")

class AdminEditInterface(AdminRequestHandler):
    def render_interface(self, model):
        self._render_interface(model)

    def _render_interface(self, model, exclude_props=[], options={}):
        model_dict = model.to_dict(exclude=exclude_props)
        #default_options = {
                #"type": "input",
                #"input_type": "text",
                #}

        #for prop, p_options in options:
            #if prop not in model_dict:
                #raise Exception("Options invalid, option key must be a valid property of the model.")
            #for option, val in default_options.items():
                #if option not in p_options:
                    #options[option] = val

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

