from django.db import models
from django.urls import reverse

from select_multiple_field.models import SelectMultipleField


class TaggedItem(models.Model):
    """Tagged item for ORM query testing"""

    TAG_CHOICES = [
        ("python", "Python"),
        ("django", "Django"),
        ("api", "API"),
        ("web", "Web"),
        ("db", "Database"),
        ("async", "Async"),
        ("orm", "ORM"),
        ("sql", "SQL"),
    ]

    name = models.CharField(max_length=100)
    tags = SelectMultipleField(
        max_length=50,
        choices=TAG_CHOICES,
        blank=True,
    )
    category = models.CharField(
        max_length=20,
        choices=[("tech", "Tech"), ("tutorial", "Tutorial")],
        blank=True,
        default="tech",
    )

    class Meta:
        app_label = "orm_test"
        ordering = ["pk"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("orm:detail", args=[self.pk])


class Article(models.Model):
    """Article with nullable tags for null query testing"""

    TAG_CHOICES = [
        ("new", "New"),
        ("sale", "Sale"),
        ("popular", "Popular"),
        ("limited", "Limited"),
    ]

    title = models.CharField(max_length=100)
    optional_tags = SelectMultipleField(
        max_length=30,
        choices=TAG_CHOICES,
        blank=True,
        null=True,
    )

    class Meta:
        app_label = "orm_test"
        ordering = ["pk"]

    def __str__(self):
        return self.title