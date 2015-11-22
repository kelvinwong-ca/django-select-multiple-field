# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

from forthewing.models import show_flavour


register = template.Library()


def decode_order(order):
    """
    Decode chicken wings order flavour list
    """
    decoded = [show_flavour(f) for f in order]
    decoded.sort()
    return ', '.join(decoded)

register.filter('decode_order', decode_order)


def decode_flavour(flavour):
    """
    Decode a single chicken wings flavour
    """
    return show_flavour(flavour)

register.filter('decode_flavour', decode_flavour)
