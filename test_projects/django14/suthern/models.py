# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import (
    force_text, python_2_unicode_compatible)
from django.utils.translation import ugettext_lazy as _

from select_multiple_field.models import SelectMultipleField


@python_2_unicode_compatible
class ChickenBalls(models.Model):
    """ChickenBalls is used for South migration testing"""

    SUICIDE = 's'
    HOT = 'h'
    HOME_STYLE = 'H'
    CAJUN = 'c'
    JERK = 'j'
    GATOR = 'g'
    FLAVOUR_CHOICES = (
        (_('Hot & Spicy'), (
            (SUICIDE, _('Suicide hot')),
            (HOT, _('Hot hot sauce')),
            (CAJUN, _('Cajun sauce')),
            (JERK, _('Jerk sauce')))),
        (_('Traditional'), (
            (HOME_STYLE, _('Homestyle')),
            (GATOR, _('Gator flavour')))),
    )
    flavour = SelectMultipleField(
        blank=True,
        include_blank=False,
        max_length=5,
        max_choices=2,
        choices=FLAVOUR_CHOICES
    )
    RANCH = 'r'
    HONEY_MUSTARD = 'h'
    BBQ = 'b'
    DIP_CHOICES = (
        (RANCH, _('Ranch')),
        (HONEY_MUSTARD, _('Honey mustard')),
        (BBQ, _('BBQ')),
    )
    dips = SelectMultipleField(
        blank=True,
        default='',
        include_blank=False,
        max_length=6,
        max_choices=3,
        choices=DIP_CHOICES
    )

    def __str__(self):
        return "pk=%s" % force_text(self.pk)

    def get_absolute_url(self):
        return reverse('ftw:detail', args=[self.pk])
