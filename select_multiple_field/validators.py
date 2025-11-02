

from django.core import validators
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

try:
    from django.utils.deconstruct import deconstructible
except ImportError:

    def deconstructible(x):
        return x


from .codecs import encode_list_to_csv


@deconstructible
class MaxChoicesValidator(validators.BaseValidator):

    message = _(
        "Ensure this value has at most %(limit_value)d choice (it has %(show_value)d).",  # NOQA
        "Ensure this value has at most %(limit_value)d choices (it has %(show_value)d).",  # NOQA
        "limit_value",
    )
    code = "max_choices"

    def compare(self, a, b):
        return a > b

    def clean(self, x):
        return len(x)


@deconstructible
class MaxLengthValidator(validators.BaseValidator):

    message = _(
        "Ensure this value has at most %(limit_value)d character (it has %(show_value)d).",  # NOQA
        "Ensure this value has at most %(limit_value)d characters (it has %(show_value)d).",  # NOQA
        "limit_value",
    )
    code = "max_length"

    def compare(self, a, b):
        return a > b

    def clean(self, value):
        return len(force_str(encode_list_to_csv(value)))
