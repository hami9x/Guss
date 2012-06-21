import logging
from google.appengine.ext import ndb
import validators

class ValidationEngine:
    errors = {}
    def __init__(self, model):
        self.model = model

    """Validate a form field with the validators in the validators module, errors are saved into
    the self.errors dictionary"""
    def validate(self, field, method, *args):
        field_value = getattr(self.model, field)
        logging.info(">>> "+field+"<<<; field_value: "+str(field_value))
        try:
            getattr(validators, "validate_"+method)(field_value, *args)
        except validators.ValidationError as e:
            if self.errors[field] == None:
                self.errors[field] = []
            self.errors[field].append(e.message)

    def has_error(self):
        return bool(self.errors)

class FormModel(ndb.Model):
    def __init__(self, *args, **kwds):
        super(FormModel, self).__init__(*args, **kwds)
        self.validations = ValidationEngine(self)

    def get_errors(self):
        return self.validations.errors

    """This method is for child classes to derive and define the validations"""
    def _validation(self):
        pass

    def validate(self):
        v_list = self._validation()
        for item in v_list:
            self.validations.validate(*item)
        return not self.validations.has_error()

    def assign(self, rhandler):
        data = rhandler.request.POST.dict_of_lists()
        for item in data.iteritems():
            field = item[0]
            if getattr(self, field, None) != None: #Model has the attribute named the same with the POST field name
                vlist = item[1]
                setattr(self, field, vlist[0] if len(vlist)<2 else vlist)


class UnsavedProperty(object):
    _value = ""
