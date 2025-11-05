from django.db import models
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _

from select_multiple_field.models import SelectMultipleField


class Pizza(models.Model):
    """Pizza demonstrates minimal use-case"""

    ANCHOVIES = "a"
    BLACK_OLIVES = "b"
    CHEDDAR_CHEESE = "c"
    EGG = "e"
    PANCETTA = "pk"
    PEPPERONI = "p"
    PROSCIUTTO_CRUDO = "P"
    MOZZARELLA = "m"
    MUSHROOMS = "M"
    TOMATO = "t"
    TOPPING_CHOICES = (
        (ANCHOVIES, _("Anchovies")),
        (BLACK_OLIVES, _("Black olives")),
        (CHEDDAR_CHEESE, _("Cheddar cheese")),
        (EGG, _("Eggs")),
        (PANCETTA, _("Pancetta")),
        (PEPPERONI, _("Pepperoni")),
        (PROSCIUTTO_CRUDO, _("Prosciutto crudo")),
        (MOZZARELLA, _("Mozzarella")),
        (MUSHROOMS, _("Mushrooms")),
        (TOMATO, _("Tomato")),
    )

    toppings = SelectMultipleField(max_length=10, choices=TOPPING_CHOICES)

    class Meta:
        verbose_name = _("Pizza")
        verbose_name_plural = _("Pizzas")
        ordering = ["pk"]

    def get_toppings(self):
        if self.toppings:
            keys_choices = self.toppings
            return "%s" % (", ".join(filter(bool, keys_choices)))

    get_toppings.short_description = _("Toppings")

    def __str__(self):
        return "pk=%s" % force_str(self.pk)

    def get_absolute_url(self):
        return reverse("pizza:detail", args=[self.pk])


def show_topping(ingredient):
    """
    Decode topping to full name
    """
    decoder = dict(Pizza.TOPPING_CHOICES)
    return force_str(decoder[ingredient])
