import warnings

from django.core import validators
from django.forms import fields

from .codecs import decode_csv_to_list, encode_list_to_csv
from .widgets import SelectMultipleWidget

DEFAULT_MAX_CHOICES_ATTR = "data-max-choices"


class SelectMultipleFormField(fields.MultipleChoiceField):

    widget = SelectMultipleWidget

    def __init__(
        self,
        max_length=None,
        size=4,
        max_choices=None,
        max_choices_attr=DEFAULT_MAX_CHOICES_ATTR,
        *args,
        **kwargs,
    ):
        """
        SelectMultipleFormField rejects items with no answer by default

        max_length refers to number of characters used to store the encoded
        list of choices (est. 2n - 1)

        size is the HTML element size attribute passed to the widget

        max_choices is the maximum number of choices allowed by the field

        max_choices_attr is a string used as an attribute name in the widget
        representation of max_choices (currently a data attribute)

        empty_value is the value used to represent an empty field

        include_blank is deprecated and will be removed in a future release.
        Use choices=[('', '---------'), ...] instead.
        """
        self.max_length, self.max_choices = max_length, max_choices
        self.size, self.max_choices_attr = size, max_choices_attr
        self.empty_value = kwargs.pop("empty_value", [])
        if "include_blank" in kwargs:
            warnings.warn(
                "include_blank is deprecated; use choices=[('', '---------'), ...] instead",
                DeprecationWarning,
                stacklevel=2,
            )
            self.include_blank = kwargs.pop("include_blank")
        if not hasattr(self, "empty_values"):
            self.empty_values = list(validators.EMPTY_VALUES)
        super(SelectMultipleFormField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Convert widget value to a Python list.

        Handles lists, tuples, CSV strings, and empty values.

        Returns list.
        """
        if isinstance(value, (list, tuple)):
            if all(v in self.empty_values for v in value):
                try:
                    # must be iterable - return a copy to avoid shared mutable state
                    iter(self.empty_value)
                    return list(self.empty_value)
                except TypeError:
                    return []

        elif (value == self.empty_value) or (value in self.empty_values):
            try:
                # must be iterable - return a copy to avoid shared mutable state
                iter(self.empty_value)
                return list(self.empty_value)
            except TypeError:
                return []

        if isinstance(value, str):
            if len(value) == 0:
                return []

            native = decode_csv_to_list(value)
            return native

        return list(value)

    def get_prep_value(self, value):
        """
        Prepares a string for use in serializer
        """
        if isinstance(value, (list, tuple)):
            if len(value) == 0:
                return ""
            else:
                return encode_list_to_csv(value)

        return ""

    def get_choices(self, **kwargs):
        """
        Choices from model without initial blank choices

        ie Stop widget from producing <option value="">---------</option>
        """
        if hasattr(self, "include_blank"):
            #
            # include_blank is deprecated and will be removed in a future release.
            #
            include_blank = self.include_blank
            if "include_blank" in kwargs:
                kwargs.pop("include_blank")
        else:
            include_blank = kwargs.pop("include_blank", False)

        if hasattr(super(), "get_choices"):
            field_options = {"include_blank": include_blank}
            field_options.update(kwargs)
            choices = super(SelectMultipleFormField, self).get_choices(**field_options)
            return list(choices)
        else:
            return list(self.choices)

    def widget_attrs(self, widget):
        """
        Given a Widget instance (*not* a Widget class), returns a dictionary of
        any HTML attributes that should be added to the Widget, based on this
        Field.
        """
        attrs = super(SelectMultipleFormField, self).widget_attrs(widget)
        if self.size != 4:
            attrs.update({"size": str(self.size)})

        if self.max_choices:
            attrs.update({self.max_choices_attr: str(self.max_choices)})

        return attrs
