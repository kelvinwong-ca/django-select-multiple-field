import sys

import django
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode

from .models import ChickenWings, show_flavour


def safe_assert_redirects(test_case, response, expected_url):
    """
    Helper function to handle assertRedirects with Python 3.14 + Django 4.2 compatibility.

    Python 3.14 + Django 4.2 has a known compatibility issue with template context copying
    that affects assertRedirects. This function provides a workaround.
    """
    if sys.version_info >= (3, 14) and django.VERSION[:2] == (4, 2):
        # For Python 3.14 + Django 4.2, just verify redirect status and location manually
        test_case.assertEqual(response.status_code, 302)
        test_case.assertEqual(response.url, expected_url)
    else:
        test_case.assertRedirects(response, expected_url)


class ChickenWingsListViewTestCase(TestCase):

    def test_no_chickenwings(self):
        p = ChickenWings.objects.all()
        self.assertEqual(len(p), 0, "Test requires no wings")
        response = self.client.get(reverse("ftw:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("No chicken wings found" in response.content.decode("utf-8"))

    def test_many_chickenwings(self):
        NUM_WINGS = 30
        wings = []
        for n in range(NUM_WINGS):
            p = ChickenWings.objects.create(flavour=[ChickenWings.HONEY_BBQ])
            wings.append(p)

        self.assertEqual(len(wings), NUM_WINGS, "Test requires chicken wings")
        response = self.client.get(reverse("ftw:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue((ChickenWings.HONEY_BBQ) in response.content.decode("utf-8"))


class ChickenWingsCreateViewTestCase(TestCase):

    def test_view(self):
        response = self.client.get(reverse("ftw:create"))
        self.assertEqual(response.status_code, 200)

    def test_creation_single(self):
        data = {"flavour": [ChickenWings.JERK]}
        response = self.client.post(
            reverse("ftw:create"),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        safe_assert_redirects(self, response, reverse("ftw:created"))
        p = ChickenWings.objects.all()[0]
        self.assertIn(ChickenWings.JERK, p.flavour)

    def test_creation_two_choices(self):
        data = {"flavour": [ChickenWings.SUICIDE, ChickenWings.BOURBON]}
        response = self.client.post(
            reverse("ftw:create"),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        safe_assert_redirects(self, response, reverse("ftw:created"))
        p = ChickenWings.objects.all()[0]
        self.assertIn(ChickenWings.SUICIDE, p.flavour)
        self.assertIn(ChickenWings.BOURBON, p.flavour)

    def test_creation_too_many_choices(self):
        data = {
            "flavour": [ChickenWings.CAJUN, ChickenWings.BOURBON, ChickenWings.MILD]
        }
        response = self.client.post(
            reverse("ftw:create"),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("flavour", response.context["form"].errors)
        self.assertEqual(len(response.context["form"].errors), 1)


class ChickenWingsDetailViewTestCase(TestCase):

    def setUp(self):
        self.chickenwings = ChickenWings(flavour=[ChickenWings.HOT])
        self.chickenwings.save()

    def test_view(self):
        response = self.client.get(reverse("ftw:detail", args=[self.chickenwings.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], self.chickenwings)


class ChickenWingsUpdateViewTestCase(TestCase):

    def setUp(self):
        self.chickenwings = ChickenWings(
            flavour=[ChickenWings.MEDIUM, ChickenWings.THAI]
        )
        self.chickenwings.save()

    def test_change_flavour(self):
        data = {"flavour": [ChickenWings.MEDIUM, ChickenWings.BACON]}
        response = self.client.post(
            reverse("ftw:update", args=[self.chickenwings.id]),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        safe_assert_redirects(self, response, reverse("ftw:updated"))
        p = ChickenWings.objects.all()[0]
        self.assertTrue(ChickenWings.MEDIUM in p.flavour)
        self.assertFalse(ChickenWings.THAI in p.flavour)
        self.assertTrue(ChickenWings.BACON in p.flavour)


class ChickenWingsDeleteViewTestCase(TestCase):

    def setUp(self):
        self.chickenwings = ChickenWings(flavour=[ChickenWings.HONEY_GARLIC])
        self.chickenwings.save()

    def test_delete_chickenwings(self):
        response = self.client.post(reverse("ftw:delete", args=[self.chickenwings.id]))
        safe_assert_redirects(self, response, reverse("ftw:deleted"))
        pl = ChickenWings.objects.all()
        self.assertEqual(len(pl), 0)


class ChickenWingsModelTestCase(SimpleTestCase):

    def test_show_flavour(self):
        for k, v in ChickenWings.FLAVOUR_CHOICES:
            if isinstance(v, (list, tuple)):
                for ko, vo in v:
                    flavour_name = show_flavour(ko)
                    self.assertEqual(flavour_name, vo)
            else:
                flavour_name = show_flavour(k)
                self.assertEqual(flavour_name, v)
