import re
from django.core.validators import email_re
from webapp2_extras.i18n import _lazy as _

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

class Validator(object):
    def __init__(self, pattern=r'', message=u""):
        self.pattern = pattern
        self.message = message

    def __call__(self, value):
        if value == "": return
        if not re.match(self.pattern, value):
            raise ValidationError(self.message)

word_re = r'^\w*$'
validate_word = Validator(word_re, _(u"Only alphanumeric letters (A-Z, a-z, 0-9)"
            " and understore (_) are allowed."))

validate_email = Validator(email_re, _(u"Please enter a valid email address"))

password_re = r'^.*(?=.*[a-zA-Z])(?=.*\d).*$'
validate_password = Validator(password_re, _(u"Must contain letters and digits"))

class MinLengthValidator(Validator):
    def __init__(self, message=_(u"Must contain at least %(length)d characters")):
        super(MinLengthValidator, self).__init__(message=message)

    def __call__(self, value, length):
        if len(value) < length:
            raise ValidationError(self.message % {"length": length})
validate_min_length = MinLengthValidator()

class TheSameValidator(Validator):
    def __init__(self, message=_(u"%(name1)s and %(name2)s must be the same")):
        super(TheSameValidator, self).__init__(message=message)

    def __call__(self, value1, value2, name1="", name2=""):
        if value1 != value2:
            raise ValidationError(self.message % {"name1": name1, "name2": name2})
validate_the_same = TheSameValidator()

validate_confirm_password = TheSameValidator(message=_(u"The passwords you entered do not match, please try again"))

class RequiredValidator(MinLengthValidator):
    def __call__(self, value):
        super(RequiredValidator, self).__call__(value, 1)
validate_required = RequiredValidator(u"Cannot be blank")
