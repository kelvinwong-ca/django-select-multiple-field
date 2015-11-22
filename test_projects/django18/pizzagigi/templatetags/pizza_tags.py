# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

from pizzagigi.models import show_topping


register = template.Library()


def decode_pie(ingredients):
    """
    Decode pizza pie toppings
    """
    decoded = [show_topping(t) for t in ingredients]
    decoded.sort()
    return ', '.join(decoded)

register.filter('decode_pie', decode_pie)


def decode_topping(ingredient):
    """
    Decode a single pizza pie topping
    """
    return show_topping(ingredient)

register.filter('decode_topping', decode_topping)
