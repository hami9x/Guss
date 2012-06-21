import re
from django.core.validators import email_re
from webapp2_extras.i18n import _lazy as _

class ValidationError(Exception):
    def __init__(self, message):
        self.message = message

class Validator:
    def __init__(self, pattern=r'', message=u""):
        self.pattern = pattern
        self.message = message

    def __call__(self, value):
        if not re.match(self.pattern, value):
            raise ValidationError(self.message)

word_re = r'^\w+$'
validate_word = Validator(word_re, _(u"Only alphanumeric letters (A-Z, a-z, 0-9) \
            and understore (_) are allowed."))

validate_email = Validator(email_re, _(u"Please enter a valid email address"))

password_re = r'^.*(?=.*[a-zA-Z])(?=.*\d).*$'
validate_password = Validator(password_re, _(u"Must contain letters and digits"))

def validate_min_length(value, length):
    if len(value) < length:
        raise ValidationError(_(u"Must contain at least %(length)d characters", length=length))

def validate_equal(value1, value2, name1, name2):
    if value1 != value2:
        raise ValidationError(_(u"%(n1)s and %(n2)s doesn't match", n1=name1, n2=name2))
