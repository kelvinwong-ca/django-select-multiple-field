from django.forms import widgets


HTML_ATTR_CLASS = "select-multiple-field"


class SelectMultipleField(widgets.SelectMultiple):
    """Multiple select widget ready for jQuery multiselect.js"""

    allow_multiple_selected = True

    def render(self, name, value, attrs=None, choices=(), renderer=None):
        rendered_attrs = {"class": HTML_ATTR_CLASS}
        if attrs:
            rendered_attrs.update(attrs)
        if value is None:
            value = []

        # Set choices if provided
        if choices:
            self.choices = choices

        # Use parent's render method and just ensure our class is added
        if renderer is not None:
            # Pass renderer parameter for Django 5.x compatibility
            return super().render(name, value, attrs=rendered_attrs, renderer=renderer)
        else:
            # Fallback for Django < 5.x
            return super().render(name, value, attrs=rendered_attrs)

    def value_from_datadict(self, data, files, name):
        """
        SelectMultipleField widget delegates processing of raw user data to
        Django's SelectMultiple widget

        Returns list or None
        """
        return super(SelectMultipleField, self).value_from_datadict(data, files, name)
