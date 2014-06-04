# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core import validators
from django.forms import fields
from django.utils import six

from .codecs import decode_csv_to_list
from .widgets import SelectMultipleField


DEFAULT_DELIMITER = ','
DEFAULT_MAX_CHOICES_ATTR = 'data-max-choices'


class SelectMultipleFormField(fields.MultipleChoiceField):

    widget = SelectMultipleField

    def __init__(
            self, max_length=None, max_choices=None, size=4,
            max_choices_attr=DEFAULT_MAX_CHOICES_ATTR,
            *args, **kwargs):
        self.max_length, self.max_choices = max_length, max_choices
        self.size, self.max_choices_attr = size, max_choices_attr
        self.coerce = kwargs.pop('coerce', lambda val: val)
        self.empty_value = kwargs.pop('empty_value', [])
        kwargs.setdefault('widget', self.widget)
        super(SelectMultipleFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Takes processed widget data as value, possibly a char string, and
        makes it into a Python list

        Returns a Python list

        Method also handles lists and strings
        """
        if value in validators.EMPTY_VALUES:
            return []

        if isinstance(value, six.string_types):
            if len(value) == 0:
                return []

            native = decode_csv_to_list(value)
            return native

        return list(value)

    def _coerce(self, value):
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

    # def validate(self, value):
    #     checked_out = True
    #     for val in value:
    #         if not self.valid_value(val):
    #             checked_out = False
    #
    #     return super(SelectMultipleFormField, self).validate(value)

    def widget_attrs(self, widget):
        """
        Given a Widget instance (*not* a Widget class), returns a dictionary of
        any HTML attributes that should be added to the Widget, based on this
        Field.
        """
        attrs = super(SelectMultipleFormField, self).widget_attrs(widget)
        if self.size != 4:
            attrs.update({'size': str(self.size)})

        if self.max_choices:
            attrs.update({self.max_choices_attr: str(self.max_choices)})

        return attrs
