import warnings

from django.forms import widgets

HTML_ATTR_CLASS = "select-multiple-field"


class SelectMultipleWidget(widgets.SelectMultiple):
    """Multiple select widget ready for jQuery multiselect.js"""

    allow_multiple_selected = True

    def render(self, name, value, attrs=None, choices=(), renderer=None):
        rendered_attrs = {"class": HTML_ATTR_CLASS}
        if attrs:
            rendered_attrs.update(attrs)
        if value is None:
            value = []

        original_choices = self.choices
        try:
            if choices:
                self.choices = choices
            if renderer is not None:
                return super().render(
                    name, value, attrs=rendered_attrs, renderer=renderer
                )
            else:
                return super().render(name, value, attrs=rendered_attrs)
        finally:
            self.choices = original_choices

    def value_from_datadict(self, data, files, name):
        """
        SelectMultipleWidget delegates processing of raw user data to
        Django's SelectMultiple widget

        Returns list or None
        """
        return super().value_from_datadict(data, files, name)


class SelectMultipleField(SelectMultipleWidget):
    """Deprecated — use SelectMultipleWidget instead."""

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SelectMultipleField is deprecated; use SelectMultipleWidget instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
