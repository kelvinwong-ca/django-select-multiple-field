# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import (
    force_text, python_2_unicode_compatible)
from django.utils.translation import ugettext_lazy as _

from select_multiple_field.models import SelectMultipleField


@python_2_unicode_compatible
class ChickenWings(models.Model):
    """ChickenWings demonstrates optgroup usage and max_choices"""

    SUICIDE = 's'
    HOT = 'h'
    MEDIUM = 'm'
    MILD = 'M'
    CAJUN = 'c'
    JERK = 'j'
    HONEY_GARLIC = 'g'
    HONEY_BBQ = 'H'
    THAI = 't'
    BACON = 'b'
    BOURBON = 'B'
    FLAVOUR_CHOICES = (
        (_('Hot & Spicy'), (
            (SUICIDE, _('Suicide hot')),
            (HOT, _('Hot hot sauce')),
            (MEDIUM, _('Medium hot sauce')),
            (MILD, _('Mild hot sauce')),
            (CAJUN, _('Cajun sauce')),
            (JERK, _('Jerk sauce')))),
        (_('Sweets'), (
            (HONEY_GARLIC, _('Honey garlic')),
            (HONEY_BBQ, _('Honey barbeque')),
            (THAI, _('Thai sweet sauce')),
            (BACON, _('Messy bacon sauce')),
            (BOURBON, _('Bourbon whiskey barbeque')))),
    )
    flavour = SelectMultipleField(
        blank=True,
        include_blank=False,
        max_length=5,
        max_choices=2,
        choices=FLAVOUR_CHOICES
    )

    def __str__(self):
        return "pk=%s" % force_text(self.pk)

    def get_absolute_url(self):
        return reverse('ftw:detail', args=[self.pk])


def show_flavour(flavour):
    """
    Decode flavour to full name

    This supports both plain choices and optgroup choices
    """
    decoder = dict()
    for c in ChickenWings.FLAVOUR_CHOICES:
        if isinstance(c[1], (tuple, list)):
            for k, v in c[1]:
                decoder[k] = v
        else:
            decoder[c[0]] = c[1]

    if flavour in decoder:
        return force_text(decoder[flavour])
    else:
        return force_text('')
