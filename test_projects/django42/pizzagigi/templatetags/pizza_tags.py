from django import template
from pizzagigi.models import show_dip, show_topping

register = template.Library()


def decode_pie(ingredients):
    """
    Decode pizza pie toppings
    """
    decoded = [show_topping(t) for t in ingredients]
    decoded.sort()
    return ", ".join(decoded)


register.filter("decode_pie", decode_pie)


def decode_topping(ingredient):
    """
    Decode a single pizza pie topping
    """
    return show_topping(ingredient)


register.filter("decode_topping", decode_topping)


def decode_dip(dip):
    """
    Decode a single pizza dip
    """
    return show_dip(dip)


register.filter("decode_dip", decode_dip)
