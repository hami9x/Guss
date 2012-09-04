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

def can_user_edit_post(handler, model):
    return (
            (   handler.current_user_check_permission("edit_own_post")
                and (handler.get_current_user().key == model.author_key())
            )
            or handler.current_user_check_permission("edit_all_post")
        )

class MasterPostEditHandler(RequestHandler):
    def _settings(self, template, model_cls, uri_id):
        self._template_name = template
        self._model_cls = model_cls
        self._uri_id = uri_id

    def settings(self):
        raise Exception("Must be overridden.")

    def _check_permission(self):
        return can_user_edit_post(self, self._thepost)

    def _handler_init(self, slug=""):
        self.settings()
        self._post_slug = slug
        postid = self.request.get("__id")
        def fn_invalid():
            self.render("noticepage", {
                "message": _(u"This post does not exist."),
                })
            self.stop()

        if postid:
            self._thepost = self._model_cls.get_by_id(int(postid))
            if self._thepost == None:
                return fn_invalid()
        else:
            if self._post_slug:
                self._thepost = self._model_cls.query(self._model_cls.slug == self._post_slug).get()
                if self._thepost == None:
                    return fn_invalid()
                postid = self._thepost.key.id()
            else:
                self._thepost = self._model_cls(title="", content="")
                if self.logged_in():
                    self._thepost.author = self.get_current_user().key
        self._postid = postid

    def template_values(self):
        return {
                "model": self._thepost,
                "postid": self._postid,
                }

    def _get(self, *args, **kwds):
        return self.render(self._template_name, self.template_values())

    def _post(self, *args, **kwds):
        post = self._thepost
        post.assign(self)
        if post.validate():
            if not post.slug:
                post.make_slug()
            post.put()

        if not self._post_slug:
            self.redirect(self.uri_for(self._uri_id, slug=post.slug))
        else:
            return self.render(self._template_name, self.template_values())

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
