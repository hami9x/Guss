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
import utils

def can_user_edit_post(handler, model):
    return (
            (   handler.current_user_check_permission("edit_own_post")
                and (handler.get_current_user().key == model.author_key())
            )
            or handler.current_user_check_permission("edit_all_post")
        )

class MasterPostEditHandler(RequestHandler):
    settings = utils.ObjectSettings()

    def _check_permission(self):
        return can_user_edit_post(self, self.the_post())

    @property
    def post_cls(self):
        return self.settings.post_cls

    @utils.cache_to_property("_the_post")
    def the_post(self, slug):
        if slug:
            return self.post_cls.query(self.post_cls.slug == slug).get()
        else:
            post = self.post_cls(title="", content="")
            if self.logged_in():
                post.author = self.get_current_user().key
            return post

    def _handler_init(self, slug=""):
        if self.the_post(slug) is None:
            self.render("noticepage", {
                "message": _(u"This post does not exist."),
                })
            self.stop()

    def template_values(self):
        return {
                "model": self.the_post(),
                }

    def _get(self, *args, **kwds):
        return self.render(self.settings.template_name, self.template_values())

    def _post(self, slug=""):
        post = self.the_post()
        post.assign(self)
        if post.validate():
            if not post.slug:
                post.make_slug()
            post.put()

        if not slug:
            self.redirect(self.uri_for(self.settings.uri_id, slug=post.slug))
        else:
            return self.render(self.settings.template_name, self.template_values())

class PostViewHandler(RequestHandler):
    def _handler_init(self, *args, **kwds):
        self.settings()

    def _settings(self, template, model_cls, slave_model_cls, edit_uri_id):
        self._template_name = template
        self._model_cls = model_cls
        self._slave_model_cls = slave_model_cls
        self._edit_uri_id = edit_uri_id

    def settings(self):
        raise Exception("Must be overridden.")

    def _check_permission(self):
        return self.current_user_check_permission("view_post")

    def _additional_values(self):
        return {}

    def _render_values(self, post, slug, slave_model=None, additional_values={}):
        """Don't-Repeat-Myself helper"""
        d = {
            "model": post,
            "can_edit": lambda: can_user_edit_post(self, post),
            "edit_url": self.uri_for(self._edit_uri_id, slug=slug),
            "slave_pagin": self._slave_pagination(post),
            "slave_model": slave_model or self._slave_model_cls(),
            }
        d.update(additional_values or self._additional_values())
        return d

    def _get(self, slug=""):
        post = self._model_cls.query(self._model_cls.slug == slug).get()
        if post == None:
            return self.render("noticepage", {
                "message": _(u"This post does not exist."),
                })
        else:
            self.render(self._template_name, self._render_values(post, slug))

    def _get_post_from_form(self):
        return self._model_cls.get_by_id(int(self.request.get("__master")))

    def _post(self, slug=""):
        raise Exception("Must be overridden.")
