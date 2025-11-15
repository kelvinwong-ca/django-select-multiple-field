from django import forms
from django.utils.translation import gettext_lazy as _

from select_multiple_field.forms import SelectMultipleFormField

DIP_CHOICES = [
    (RANCH := "r", _("Ranch")),
    (BLUE_CHEESE := "b", _("Blue Cheese")),
    (HONEY_MUSTARD := "h", _("Honey Mustard")),
]


class DipsForm(forms.Form):
    """Form to test blank choices selection"""

    dips = SelectMultipleFormField(
        choices=DIP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
