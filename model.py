from google.appengine.ext import ndb
import validators

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

    """Validate a form field with the validators in the validators module, errors are saved into
    the self.errors dictionary"""
    def validate(self, field, method, *args):
        field_value = getattr(self.model, field)
        try:
            getattr(validators, "validate_"+method)(field_value, *args)
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
        if not self._validated:
            self.validate()
        return self.validations.errors

    """This method is for child classes to derive and define the validations"""
    def _validation(self):
        pass

    def validate(self):
        v_list = self._validation()
        for item in v_list:
            self.validations.validate(*item)
        self._validated = True
        return not self.validations.has_error()

    def assign(self, rhandler):
        data = rhandler.request.POST.dict_of_lists()
        for field, vlist in data.iteritems():
            if hasattr(self, field): #Model has the attribute named the same with the POST field name
                setattr(self, field, vlist[0] if len(vlist)<2 else vlist)

    def get_verbose_name(self, attr):
        if attr in self._properties:
            return self._properties[attr]._verbose_name
        elif attr in self._unsaved_properties:
            return self._unsaved_properties[attr]._verbose_name
        else:
            raise AttributeError("FormModel instance has no attribute %s" % attr)
