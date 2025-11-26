from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_str
from django.utils.translation import ngettext_lazy

from .codecs import encode_list_to_csv


@deconstructible
class MaxChoicesValidator(validators.BaseValidator):

    message = ngettext_lazy(
        "Ensure this value has at most %(limit_value)d choice (it has %(show_value)d).",
        "Ensure this value has at most %(limit_value)d choices (it has %(show_value)d).",
        "limit_value",
    )
    code = "max_choices"

    def compare(self, a, b):
        return a > b

    def clean(self, x):
        return len(x)


@deconstructible
class MaxLengthValidator(validators.BaseValidator):
    """
    Validates that the encoded CSV string length does not exceed max_length.

    Since this field stores data as a CSV string in a CharField, max_length
    refers to the database column width. The validator encodes the list to
    CSV to measure the actual stored length. The double encoding (here +
    get_prep_value) is standard — validators operate on Python values.
    """

    message = ngettext_lazy(
        "Ensure this value has at most %(limit_value)d character (it has %(show_value)d).",
        "Ensure this value has at most %(limit_value)d characters (it has %(show_value)d).",
        "limit_value",
    )
    code = "max_length"

    def compare(self, a, b):
        return a > b

    def clean(self, value):
        return len(force_str(encode_list_to_csv(value)))
