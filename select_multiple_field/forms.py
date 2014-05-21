# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.forms import fields
# from django.utils.translation import ugettext_lazy as _

# from .codecs import decode_csv_to_list, encode_list_to_csv
from .widgets import SelectMultipleField


DEFAULT_DELIMITER = ','


class SelectMultipleFormField(fields.TypedMultipleChoiceField):

    widget = SelectMultipleField

    def __init__(self, *args, **kwargs):

        kwargs.setdefault('widget', self.widget)
        super(SelectMultipleFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Takes database value, usually char string, and makes it into a Python
        list

        Method also handles lists and strings
        """
        delimiter = getattr(
            settings, 'SELECTMULTIPLEFIELD_DELIMITER', DEFAULT_DELIMITER)
        if value is None:
            return []
        if isinstance(value, basestring):
            return value.split(delimiter)
        return value

    def get_prep_value(self, value):
        """
        Prepares a string for use in serializer
        """
        delimiter = getattr(
            settings, 'SELECTMULTIPLEFIELD_DELIMITER', DEFAULT_DELIMITER)
        if isinstance(value, (list, tuple)):
            if len(value) == 0:
                return ''
            else:
                return delimiter.join(value)

        return ''

    def validate(self, value):
        checked_out = True
        for val in value:
            if not self.valid_value(val):
                checked_out = False

        return super(SelectMultipleFormField, self).validate(value)
