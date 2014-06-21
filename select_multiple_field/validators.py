# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import validators
from django.utils.encoding import force_text
from django.utils.translation import ungettext_lazy

try:
    from django.utils.deconstruct import deconstructible
except ImportError:
    deconstructible = lambda x: x

from .codecs import encode_list_to_csv


@deconstructible
class MaxChoicesValidator(validators.BaseValidator):
    compare = lambda self, a, b: a > b
    clean = lambda self, x: len(x)
    message = ungettext_lazy(
        'Ensure this value has at most %(limit_value)d choice (it has %(show_value)d).',  # NOQA
        'Ensure this value has at most %(limit_value)d choices (it has %(show_value)d).',  # NOQA
        'limit_value')
    code = 'max_choices'


@deconstructible
class MaxLengthValidator(validators.BaseValidator):
    compare = lambda self, a, b: a > b
    message = ungettext_lazy(
        'Ensure this value has at most %(limit_value)d character (it has %(show_value)d).',  # NOQA
        'Ensure this value has at most %(limit_value)d characters (it has %(show_value)d).',  # NOQA
        'limit_value')
    code = 'max_length'

    def clean(self, value):
        return len(force_text(encode_list_to_csv(value)))
