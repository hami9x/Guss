import random
import string
import re
from unidecode import unidecode

def generate_random_string(length):
    return "".join(random.choice(string.ascii_letters + string.digits) for x in range(length))

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u"-"):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))
