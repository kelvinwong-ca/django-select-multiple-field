# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from select_multiple_field.models import SelectMultipleField


class Pizza(models.Model):
    ANCHOVIES = 'a'
    BLACK_OLIVES = 'b'
    CHEDDAR_CHEESE = 'c'
    EGG = 'e'
    PANCETTA = 'pk'
    PEPPERONI = 'p'
    PROSCIUTTO_CRUDO = 'P'
    MOZZARELLA = 'm'
    MUSHROOMS = 'M'
    TOMATO = 't'
    TOPPING_CHOICES = (
        (ANCHOVIES, _('Anchovies')),
        (BLACK_OLIVES, _('Black olives')),
        (CHEDDAR_CHEESE, _('Cheddar cheese')),
        (EGG, _('Eggs')),
        (PANCETTA, _('Pancetta')),
        (PEPPERONI, _('Pepperoni')),
        (PROSCIUTTO_CRUDO, _('Prosciutto crudo')),
        (MOZZARELLA, _('Mozzarella')),
        (MUSHROOMS, _('Mushrooms')),
        (TOMATO, _('Tomato')),
    )

    toppings = SelectMultipleField(
        max_length=10,
        choices=TOPPING_CHOICES
    )


def show_topping(ingredient):
    """
    Decode topping to full name
    """
    decoder = dict(Pizza.TOPPING_CHOICES)
    return force_unicode(decoder[ingredient])
