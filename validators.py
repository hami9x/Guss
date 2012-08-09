import re
from django.core.validators import email_re
from webapp2_extras.i18n import _lazy as _

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

class Validator(object):
    def __init__(self, pattern=r''):
        self.pattern = pattern

    def message(self):
        raise Exception("validator message is not defined")

    def _raise(self):
        raise ValidationError(self.message())

    def __call__(self, value):
        if not re.match(self.pattern, value):
            self._raise()

word_re = r'^\w*$'
validate_word = Validator(word_re)
validate_word.message = lambda: _(u"Only alphanumeric letters (A-Z, a-z, 0-9)"
            " and understore (_) are allowed.")

validate_email = Validator(email_re)
validate_email.message = lambda: _(u"Please enter a valid email address")

password_re = r'^.*(?=.*[a-zA-Z])(?=.*\d).*$'
validate_password = Validator(password_re, )
validate_password.message = lambda: _(u"Must contain letters and digits")

class MinLengthValidator(Validator):
    def message(self):
        return _(u"Must contain at least %(length)d characters")

    def __call__(self, value, length):
        if len(value) < length:
            raise ValidationError(self.message() % {"length": length})
validate_min_length = MinLengthValidator()

class MaxLengthValidator(Validator):
    def message(self):
        return _(u"Cannot contain more than %(length)d characters")

    def __call__(self, value, length):
        if len(value) > length:
            raise ValidationError(self.message() % {"length": length})
validate_max_length = MaxLengthValidator()

class TheSameValidator(Validator):
    def message(self):
        return _(u"%(name1)s and %(name2)s must be the same")

    def __call__(self, value1, value2, name1="", name2=""):
        if value1 != value2:
            raise ValidationError(self.message() % {"name1": name1, "name2": name2})
validate_the_same = TheSameValidator()

validate_confirm_password = TheSameValidator()
validate_confirm_password.message = lambda: _(u"The passwords you entered do not match, please try again")

class RequiredValidator(MinLengthValidator):
    def message(self):
        return _(u"Cannot be blank")

    def __call__(self, value):
        super(RequiredValidator, self).__call__(value, 1)
validate_required = RequiredValidator()

class CommonData(object):
    pass

class UniqueValidator(Validator):
    def message(self):
        return _(u"already taken, please choose a different one")

    def __call__(self, value):
        model = CommonData.model
        field = CommonData.field
        if (getattr(model, field) != value):
            raise Exception("""Something is wrong here, the 'value' argument is
                    different from the value of the model field""")
        cls = type(model)
        q = cls.query(getattr(cls, field)==value)
        if q.count() > 0:
            if (model.key != q.get().key):
                self._raise()
validate_unique = UniqueValidator()
