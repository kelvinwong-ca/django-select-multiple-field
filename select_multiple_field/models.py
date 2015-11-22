# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core import exceptions, validators
from django.db import models
from django.utils import six
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _

from .codecs import decode_csv_to_list, encode_list_to_csv
from .validators import MaxChoicesValidator, MaxLengthValidator
import select_multiple_field.forms as forms


DEFAULT_DELIMITER = ','


@python_2_unicode_compatible
class SelectMultipleField(six.with_metaclass(models.SubfieldBase,
                                             models.Field)):
    """Stores multiple selection choices as serialized list"""

    default_error_messages = {
        'blank': _("This field cannot be blank."),
        'invalid_type': _(
            "Types passed as value must be string, list, tuple or None, "
            "not '%(value)s'."),
        'invalid_choice': _(
            "Select a valid choice. %(value)s is not one of the available "
            "choices."),
        'null': _("This field cannot be null."),
    }
    description = _('Select multiple field')

    def __init__(self, *args, **kwargs):
        """
        SelectMultipleField rejects items with no answer by default

        By default responses are required, so 'blank' is False
        """
        if 'max_choices' in kwargs:
            self.max_choices = kwargs.pop('max_choices')

        if 'include_blank' in kwargs:
            self.include_blank = kwargs.pop('include_blank')

        super(SelectMultipleField, self).__init__(*args, **kwargs)

        self.validators.append(MaxLengthValidator(self.max_length))
        if hasattr(self, 'max_choices'):
            self.validators.append(MaxChoicesValidator(self.max_choices))

    def __str__(self):
        return "%s" % force_text(self.description)

    def get_internal_type(self):
        return "CharField"

    def to_python(self, value):
        """
        When SelectMultipleField is assigned a value, this method coerces
        into a list usable by Python

        value is Encoded strings from the database or Python native types in
        need of validation

        Raises ValidationError if value is not in choices or if invalid type

        Returns list
        """
        if value is None:
            return value

        elif isinstance(value, (list, tuple)):
            self.validate_options_list(value)
            return value

        elif isinstance(value, six.string_types):
            #
            # Strings are always encoded choices
            #
            native = decode_csv_to_list(value)
            return native

        msg = self.error_messages['invalid_type'] % {'value': type(value)}
        raise exceptions.ValidationError(msg)

    def get_prep_value(self, value):
        """
        Perform preliminary non-db specific value checks and conversions.

        This takes a Python list and encodes it into a form storable in the
        database

        Returns a string or None
        """
        if value is None:
            return None

        return encode_list_to_csv(value)

    def get_choices(self, **kwargs):
        """
        Choices from model without initial blank choices

        ie Stop widget from producing <option value="">---------</option>

        If ModelField.include_blank is set then ignore any overrides sent via
        kwargs
        """
        include_blank = False
        if hasattr(self, 'include_blank'):
            include_blank = self.include_blank
            if 'include_blank' in kwargs:
                kwargs.pop('include_blank')

        field_options = {
            'include_blank': include_blank
        }
        field_options.update(kwargs)
        return super(SelectMultipleField, self).get_choices(**field_options)

    def has_choices(self):
        """
        Check if the field has choices values bound to it
        """
        choices = getattr(self, 'choices', None)
        if choices is None:
            choices = getattr(self, '_choices', None)

        return bool(choices)

    def value_to_string(self, obj):
        """
        Used for serialization of the expected Python list
        """
        native = self._get_val_from_obj(obj)
        return native
        # return smart_text(self._get_val_from_obj(obj))  # Default code

    def validate(self, value, model_instance):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if self.has_choices() and value:
            if isinstance(value, (list, tuple)):
                bad_values = []
                for opt in value:
                    if self.blank and opt in validators.EMPTY_VALUES:
                        pass
                    elif opt not in self.get_choices_keys():
                        bad_values.append(opt)
                if len(bad_values) == 0:
                    return
                else:
                    msg = self.error_messages['invalid_choice'] % {
                        'value': bad_values}
                    raise exceptions.ValidationError(msg)

            msg = self.error_messages['invalid_choice'] % {'value': value}
            raise exceptions.ValidationError(msg)

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages['blank'])

    def validate_options_list(self, value):
        """
        Checks that all options in value list are in choices

        Raises ValidationError if an option in value list is not in choices

        Returns None if all values are in choices
        """
        for option in value:
            if not self.validate_option(option):
                msg = self.error_messages['invalid_choice'] % {'value': option}
                raise exceptions.ValidationError(msg)

        return

    def get_choices_keys(self, **kwargs):
        """
        Flattens choices and optgroup choices into a plain list of keys

        Returns choices keys as list
        """
        flat_choices = []
        choices = self.get_choices(**kwargs)
        for key, val in choices:
            if isinstance(val, (list, tuple)):
                for opt_key, opt_val in val:
                    flat_choices.append(opt_key)
            else:
                flat_choices.append(key)

        return flat_choices

    def validate_option(self, value):
        """
        Checks that value is in choices
        """
        if self.blank and value in validators.EMPTY_VALUES:
            return True

        flat_choices = self.get_choices_keys()
        return value in flat_choices

    def formfield(self, **kwargs):
        """
        This returns the correct formclass without calling super

        Returns select_multiple_field.forms.SelectMultipleFormField
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
            # Django normally includes an empty choice if blank, has_default
            # and initial are all False, we are intentially breaking this
            # convention
            include_blank = self.blank
            defaults['choices'] = self.get_choices(include_blank=include_blank)
            defaults['coerce'] = self.to_python
            if self.null:
                defaults['empty_value'] = None

            # Many of the subclass-specific formfield arguments (min_value,
            # max_value) don't apply for choice fields, so be sure to only pass
            # the values that SelectMultipleFormField will understand.
            for k in kwargs.keys():
                if k not in ('coerce', 'empty_value', 'choices', 'required',
                             'widget', 'label', 'initial', 'help_text',
                             'error_messages', 'show_hidden_initial'):
                    del kwargs[k]

        defaults.update(kwargs)
        return forms.SelectMultipleFormField(**defaults)

    def south_field_triple(self):
        try:
            from south.modelsinspector import introspector
        except ImportError:
            pass
        else:
            cls_name = '{}.{}'.format(
                self.__class__.__module__,
                self.__class__.__name__)
            args, kwargs = introspector(self)

            if hasattr(self, 'max_choices'):
                kwargs["max_choices"] = self.max_choices

            if hasattr(self, 'include_blank'):
                kwargs["include_blank"] = self.include_blank

            return (cls_name, args, kwargs)

    def deconstruct(self):
        """
        How to reduce the field to a serializable form.

        The arguments to pass to field constructor to reconstruct it.

        Returns a tuple of four items:
            the field’s attribute name,
            the full import path of the field class,
            the positional arguments (an empty list in this case),
            the keyword arguments (as a dict).
        """
        name, path, args, kwargs = super(
            SelectMultipleField, self).deconstruct()

        if hasattr(self, 'max_choices'):
            kwargs["max_choices"] = self.max_choices

        if hasattr(self, 'include_blank'):
            kwargs["include_blank"] = self.include_blank

        return (
            force_text(name, strings_only=True),
            path,
            args,
            kwargs,
        )
