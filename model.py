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

from google.appengine.ext import ndb
import validators
import hashlib

class UnsavedProperty(object):
    _value = None

    def __init__(self, verbose_name):
        self._verbose_name = verbose_name

    def __get__(self, entity, type=None):
        if entity is None: #called on class
            return self
        return self._value

    def __set__(self, entity, value):
        self._value = value

class PasswordProperty(ndb.StringProperty):
    @staticmethod
    def do_hash(str):
        m = hashlib.sha256()
        m.update(str)
        return m.hexdigest()

    def _to_base_type(self, value):
        return self.do_hash(value)

class BooleanProperty(ndb.BooleanProperty):
    def _validate(self, value):
        if value in [u"yes", "yes"]:
            value = True
        elif value in [u"no", "no"]:
            value = False
        assert type(value) == bool
        return value

class MyMetaModel(ndb.MetaModel):
    def __init__(cls, name, bases, classdict):
        super(MyMetaModel, cls).__init__(name, bases, classdict)
        #Add the UnsavedProperty's to the internal _unsaved_properties for use with get_verbose_name
        cls._unsaved_properties = {}
        for name in set(dir(cls)):
            attr = getattr(cls, name, None)
            if isinstance(attr, UnsavedProperty):
                cls._unsaved_properties[name] = attr

class ValidationEngine(object):
    def __init__(self, model):
        self.errors = {}
        self.model = model
        self._additional_inf = {
                "unique": ["model", "field"],
                }
        self._inf = {}
        self.set_inf("model", self.model)

    def set_inf(self, name, val):
        self._inf[name] = val

    def get_inf(self, name):
        return self._inf[name]

    """Validate a form field with the validators in the validators module, errors are saved into
    the self.errors dictionary"""
    def validate(self, field, method, *args):
        self.set_inf("field", field)

        field_value = getattr(self.model, field)
        #Do not perform validation if:
        #  Field is None (not used in the form)
        #  Field is left blank and this is not a "required" validation
        if (field_value is not None) and ((method == "required") or (field_value != "")):
            try:
                fn = getattr(validators, "validate_"+method)
                additional = {}
                if method in self._additional_inf:
                    for inf in self._additional_inf[method]:
                        additional[inf] = self.get_inf(inf)
                fn(field_value, *args, **additional)
            except validators.ValidationError as e:
                if not(field in self.errors):
                    self.errors[field] = []
                self.errors[field].append(e.message)

    def has_error(self):
        return bool(self.errors)

class FormModel(ndb.Model):
    __metaclass__ = MyMetaModel
    _validated = False

    def __init__(self, *args, **kwds):
        super(FormModel, self).__init__(*args, **kwds)
        self.validations = ValidationEngine(self)

    def get_errors(self):
        return self.validations.errors

    def _validation(self):
        """This method is for child classes to override and define the validations"""
        return {}

    def validate(self):
        field_dict = self._validation()
        for field, v_dict in field_dict.iteritems():
            for method, params in v_dict.iteritems():
                if not isinstance(params, tuple):
                    raise Exception("Validation parameters must be a python tuple, check your model's _validation() method")
                self.validations.validate(field, method, *params)
        self._validated = True
        return not self.validations.has_error()

    def put(self, force_validation=True):
        if force_validation:
            if not self._validated:
                self.validate()
            if self.get_errors():
                raise Exception("Cannot save to the database because there are validation errors.")
        return super(FormModel, self).put()

    def assign(self, rhandler):
        data = rhandler.request.POST.dict_of_lists()
        for field, vlist in data.iteritems():
            if hasattr(self, field): #Model has the attribute named the same as the POST field name
                setattr(self, field, vlist[0] if len(vlist)<2 else vlist)

    def get_verbose_name(self, attr):
        if attr in self._properties:
            ret = self._properties[attr]._verbose_name
        elif attr in self._unsaved_properties:
            ret = self._unsaved_properties[attr]._verbose_name
        else:
            raise AttributeError("FormModel instance has no attribute %s" % attr)
        return ret if ret != None else attr

    def is_required(self, field):
        v_dict = self._validation()
        if (field in v_dict) and ("required" in v_dict[field]):
            return True
        else: return False
