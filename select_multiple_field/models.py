# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core import exceptions, validators
from django.db import models
from django.utils import six
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from .codecs import decode_csv_to_list, encode_list_to_csv
import select_multiple_field.forms as forms


DEFAULT_DELIMITER = ','


@python_2_unicode_compatible
class SelectMultipleField(models.Field):
    """Stores multiple selection choices as serialized list"""

    description = _('Select multiple field')
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        """
        SelectMultipleField rejects items with no answer

        By default responses are required, so 'blank' is False
        """
        super(SelectMultipleField, self).__init__(*args, **kwargs)
        self.validators.append(validators.MaxLengthValidator(self.max_length))

    def __str__(self):
        return "%s" % force_text(self.description)

    def get_internal_type(self):
        return "CharField"

    def to_python(self, value):
        """
        When SelectMultipleField is assigned a value, this method coerces
        into a list usable by Python
        """
        delimiter = getattr(
            settings, 'SELECTMULTIPLEFIELD_DELIMITER', DEFAULT_DELIMITER)
        if isinstance(value, six.string_types):
            pyval = decode_csv_to_list(value)
            return pyval
        elif value is None:
            return value
        if isinstance(value, (list, tuple)):
            return value

        raise Exception('End of Model.to_python')
        return delimiter.join(value)

    def get_prep_value(self, value):
        """
        Perform preliminary non-db specific value checks and conversions.

        This takes a Python list and encodes it into a form storable in the
        database
        """
        return encode_list_to_csv(value)

    def value_from_object(self, obj):
        """
        Returns the value of this field in the given model instance.
        """
        value = getattr(obj, self.attname)
        return value

    def get_choices(self, **kwargs):
        """
        Choices without initial blank choices
        """
        field_options = {
            'include_blank': False
        }
        kwargs.update(field_options)
        return super(SelectMultipleField, self).get_choices(**kwargs)

    def validate(self, value, model_instance):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if not self.editable:
            # Skip validation for non-editable fields.
            return
        if self._choices and value:
            if isinstance(value, (list, tuple)):
                bad_values = []
                for opt in value:
                    if opt not in [choice[0] for choice in self.choices]:
                        bad_values.append(opt)
                if len(bad_values) == 0:
                    return

            for option_key, option_value in self.choices:
                if isinstance(option_value, (list, tuple)):
                    # This is an optgroup, so look inside the group for
                    # options.
                    for optgroup_key, optgroup_value in option_value:
                        if value == optgroup_key:
                            return
                elif value == option_key:
                    return
            msg = self.error_messages['invalid_choice'] % value
            raise exceptions.ValidationError(msg)

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages['blank'])

    def formfield(self, **kwargs):
        """
        This returns the right formclass without calling super
        """
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text}
        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()
        if self.choices:
            # Fields with choices get special treatment.
            include_blank = (self.blank or
                             not (self.has_default() or 'initial' in kwargs))
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            defaults['coerce'] = self.to_python
            if self.null:
                defaults['empty_value'] = None

            # Many of the subclass-specific formfield arguments (min_value,
            # max_value) don't apply for choice fields, so be sure to only pass
            # the values that TypedChoiceField will understand.
            for k in kwargs.keys():
                if k not in ('coerce', 'empty_value', 'choices', 'required',
                             'widget', 'label', 'initial', 'help_text',
                             'error_messages', 'show_hidden_initial'):
                    del kwargs[k]
        defaults.update(kwargs)
        return forms.SelectMultipleFormField(**defaults)
