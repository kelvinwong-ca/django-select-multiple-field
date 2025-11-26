import warnings

from django.core import exceptions, validators
from django.db import models
from django.utils.encoding import force_str
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

import select_multiple_field.forms as forms

from .codecs import decode_csv_to_list, encode_list_to_csv
from .validators import MaxChoicesValidator, MaxLengthValidator


class SelectMultipleField(models.CharField):
    """Stores multiple selection choices as serialized list"""

    default_error_messages = {
        "blank": _("This field cannot be blank."),
        "invalid_type": _(
            "Types passed as value must be string, list, tuple or None, "
            "not '%(value)s'."
        ),
        "invalid_choice": _(
            "Select a valid choice. %(value)s is not one of the available choices."
        ),
        "null": _("This field cannot be null."),
    }
    description = _("Select multiple field")

    def __init__(self, *args, **kwargs):
        """
        Stores selected choices as CSV in the database and as list-like values
        in Python.

        Behavior notes:

        - `blank=False` means a value is required by field validation.
        - `null=True` stores SQL NULL for empty values in the database.
        - Python-side normalization converts `None` to an empty list in
            `to_python()` / `from_db_value()` for a consistent in-memory API.
        - If `choices` and `max_choices` are set and `max_length` is omitted,
            `max_length` is computed from the longest possible encoded CSV value.
        - If `max_length` is explicitly provided but is smaller than that
            computed encoded length, a `RuntimeWarning` is emitted.

        Extra kwargs:

        - `max_choices`: optional positive integer that limits the number of
            selected options.
        """
        self.max_choices = None
        self.include_blank = False
        self._include_blank_set = False

        kwargs = kwargs.copy()

        if "max_choices" in kwargs:
            max_choices = kwargs.pop("max_choices")
            if max_choices is not None:
                if not isinstance(max_choices, int) or max_choices <= 0:
                    raise ValueError("max_choices must be a positive integer")
                self.max_choices = max_choices

        if "include_blank" in kwargs:
            #
            # include_blank is deprecated but retained for migration compatibility.
            #
            include_blank = kwargs.pop("include_blank")
            if not isinstance(include_blank, bool):
                raise TypeError("include_blank must be a boolean")
            self.include_blank = include_blank
            self._include_blank_set = True

        explicit_max_length = "max_length" in kwargs

        super(SelectMultipleField, self).__init__(*args, **kwargs)

        if self.max_length is None and self.choices and self.max_choices is not None:
            self.max_length = self._calculate_max_encoded_length()
        elif explicit_max_length and self.choices and self.max_choices is not None:
            calculated = self._calculate_max_encoded_length()
            if self.max_length < calculated:
                warnings.warn(
                    f"max_length={self.max_length} is too small for max_choices={self.max_choices} "
                    f"with choices={list(self.get_choices_keys())}. "
                    f"Encoded CSV will be up to {calculated} chars. "
                    f"Validation will fail for max selections.",
                    RuntimeWarning,
                    stacklevel=2,
                )

        self.validators = [
            v
            for v in self.validators
            if not isinstance(v, validators.MaxLengthValidator)
        ]

        self.validators.append(MaxLengthValidator(self.max_length))
        if self.max_choices is not None:
            self.validators.append(MaxChoicesValidator(self.max_choices))

    def _calculate_max_encoded_length(self):
        """
        Calculate max encoded CSV length from choices and max_choices.

        Returns the max possible length of the CSV string when max_choices
        are selected (choices joined by commas).
        """
        choice_keys = self.get_choices_keys()
        if not choice_keys:
            return 0

        sorted_keys = sorted(choice_keys, key=len, reverse=True)
        max_keys = sorted_keys[: self.max_choices]

        return len(",".join(max_keys))

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
            return []

        elif isinstance(value, (list, tuple)):
            self.validate_options_list(value)
            return value

        elif isinstance(value, str):
            #
            # Strings are always encoded choices
            #
            native = decode_csv_to_list(value)
            return native

        msg = self.error_messages["invalid_type"] % {"value": type(value)}
        raise exceptions.ValidationError(msg)

    def from_db_value(self, value, expression, connection, context=None):
        """
        Converts a value as returned by the database to a Python object.
        It is the reverse of get_prep_value().

        This should always return a Python list.
        """
        if isinstance(value, str):
            return decode_csv_to_list(value)
        return []

    def get_prep_value(self, value):
        """
        Perform preliminary non-db specific value checks and conversions.

        This takes a Python list and encodes it into a string form representable
        in the database.

        If value is already a string (e.g. from a raw ORM lookup like
        .filter(tags="django,api")), it is returned as-is to avoid
        double-encoding.

        Returns a string or None (if null=True and value is empty)
        """
        if value is None:
            return None if self.null else ""

        # Handle already-encoded CSV string (for query lookups)
        if isinstance(value, str):
            return value

        if len(value) == 0:
            if self.null:
                return None
            return ""

        return encode_list_to_csv(value)

    def get_choices(self, **kwargs):
        """
        Choices from model without initial blank choices

        ie Stop widget from producing <option value="">---------</option>

        If ModelField.include_blank is set then ignore any overrides sent via
        kwargs
        """
        include_blank = False
        if getattr(self, "_include_blank_set", False):
            include_blank = self.include_blank
            if "include_blank" in kwargs:
                kwargs.pop("include_blank")
        else:
            include_blank = kwargs.pop("include_blank", False)

        field_options = {"include_blank": include_blank}
        field_options.update(kwargs)
        choices = super(SelectMultipleField, self).get_choices(**field_options)
        # Convert to list for Django < 5.0 compatibility (parent returns iterable in 5.0+)
        return list(choices)

    def has_choices(self):
        """
        Check if the field has choices values bound to it
        """
        choices = getattr(self, "choices", None)
        if choices is None:
            choices = getattr(self, "_choices", None)

        return bool(choices)

    def value_to_string(self, obj):
        """
        Used for serialization of the expected Python list
        """
        if hasattr(self, "value_from_object"):
            native = self.value_from_object(obj)
        else:
            # Fallback for older Django versions
            native = getattr(obj, self.attname)
        return encode_list_to_csv(native)

    def validate(self, value, model_instance):
        """
        Validates value and throws ValidationError. Subclasses should override
        this to provide validation logic.
        """
        if not self.editable:
            return

        if isinstance(value, str):
            value = decode_csv_to_list(value)

        # Replicate parent Field.validate() blank/null/choice checks.
        # We don't call super().validate() because with choices set
        # and value as a list, the parent tries to match the list
        # against choice keys, which always fails for multi-select values.
        # Note: run_validators() is called by Field.clean() after validate(),
        # so we don't call it here.
        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages["blank"], code="blank")
        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages["null"], code="null")

        if self.has_choices() and value:
            if isinstance(value, (list, tuple)):
                bad_values = self._find_invalid_choices(value)
                if bad_values:
                    msg = self.error_messages["invalid_choice"] % {"value": bad_values}
                    raise exceptions.ValidationError(msg)
            else:
                msg = self.error_messages["invalid_choice"] % {"value": value}
                raise exceptions.ValidationError(msg)

    def _find_invalid_choices(self, value):
        """
        Returns a list of invalid choices in value that are not in the field's choices.
        """
        bad_values = []
        for opt in value:
            if self.blank and opt in validators.EMPTY_VALUES:
                pass
            elif opt not in self.get_choices_keys():
                bad_values.append(opt)
        return bad_values

    def validate_options_list(self, value):
        """
        Checks that all options in value list are in choices

        Raises ValidationError if an option in value list is not in choices

        Returns None if all values are in choices
        """
        bad_values = self._find_invalid_choices(value)
        if bad_values:
            msg = self.error_messages["invalid_choice"] % {"value": bad_values}
            raise exceptions.ValidationError(msg)

    def get_choices_keys(self, **kwargs):
        """
        Flattens choices and optgroup choices into a plain list of keys

        Returns choices keys as list
        """
        if not kwargs and hasattr(self, "_flat_choices_cache"):
            return self._flat_choices_cache

        choices = self.get_choices(**kwargs)
        flat = []
        for key, val in choices:
            if isinstance(val, (list, tuple)):
                for opt_key, opt_val in val:
                    flat.append(opt_key)
            else:
                flat.append(key)

        if not kwargs:
            self._flat_choices_cache = flat
        return flat

    def validate_option(self, value):
        """
        Legacy helper not used by the field's internal validation flow.

        Checks that value is in choices.
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
        defaults = {
            "required": not self.blank,
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
        }
        if self.has_default():
            if callable(self.default):
                defaults["initial"] = self.default
                defaults["show_hidden_initial"] = True
            else:
                defaults["initial"] = self.get_default()

        if self.choices:
            # Django normally includes an empty choice if blank, has_default
            # and initial are all False, we are intentionally breaking this
            # convention
            include_blank = self.blank
            defaults["choices"] = self.get_choices(include_blank=include_blank)
            if self.null:
                defaults["empty_value"] = None

            allowed = {
                "empty_value",
                "choices",
                "required",
                "widget",
                "label",
                "initial",
                "help_text",
                "error_messages",
                "show_hidden_initial",
            }
            kwargs = {k: v for k, v in kwargs.items() if k in allowed}

        defaults.update(kwargs)
        return forms.SelectMultipleFormField(**defaults)

    def deconstruct(self):
        """
        How to reduce the field to a serializable form.

        The arguments to pass to field constructor to reconstruct it.

        Returns a tuple of four items:
            the field's attribute name,
            the full import path of the field class,
            the positional arguments (an empty list in this case),
            the keyword arguments (as a dict).
        """
        name, path, args, kwargs = super(SelectMultipleField, self).deconstruct()

        if self.max_choices is not None:
            kwargs["max_choices"] = self.max_choices

        if getattr(self, "_include_blank_set", False):
            kwargs["include_blank"] = self.include_blank

        return (
            force_str(name, strings_only=True),
            path,
            args,
            kwargs,
        )
