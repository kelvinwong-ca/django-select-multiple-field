from django.db import connection
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode

from test_projects.asserts import safe_assert_redirects

from .forms import BLUE_CHEESE, HONEY_MUSTARD, RANCH, DipsForm
from .models import ChickenWings, show_flavour


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

    def test_show_flavour_unknown_key(self):
        result = show_flavour("unknown")
        self.assertEqual(result, "")

    def test_show_flavour(self):
        for k, v in ChickenWings.FLAVOUR_CHOICES:
            if isinstance(v, (list, tuple)):
                for ko, vo in v:
                    flavour_name = show_flavour(ko)
                    self.assertEqual(flavour_name, vo)
            else:
                flavour_name = show_flavour(k)
                self.assertEqual(flavour_name, v)


class ChickenWingsNullOptionalFlavourTestCase(TestCase):
    """Tests for null=True storage behavior on the optional_flavour field"""

    def test_create_with_no_optional_flavour_stores_null(self):
        """Creating wings without optional_flavour stores NULL in the database"""
        wings = ChickenWings.objects.create(flavour=[ChickenWings.HOT])
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT optional_flavour FROM forthewing_chickenwings WHERE id = %s",
                [wings.pk],
            )
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_create_with_empty_optional_flavour_stores_null(self):
        """Creating wings with empty optional_flavour list stores NULL in the database"""
        wings = ChickenWings.objects.create(
            flavour=[ChickenWings.HOT], optional_flavour=[]
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT optional_flavour FROM forthewing_chickenwings WHERE id = %s",
                [wings.pk],
            )
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_create_with_optional_flavour_stores_string(self):
        """Creating wings with optional_flavour stores an encoded string in the database"""
        wings = ChickenWings.objects.create(
            flavour=[ChickenWings.HOT], optional_flavour=[ChickenWings.JERK]
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT optional_flavour FROM forthewing_chickenwings WHERE id = %s",
                [wings.pk],
            )
            row = cursor.fetchone()
        self.assertIsInstance(row[0], str)

    def test_load_null_optional_flavour_returns_empty_list(self):
        """Loading wings with NULL optional_flavour from the database returns an empty list"""
        wings = ChickenWings.objects.create(flavour=[ChickenWings.HOT])
        wings_from_db = ChickenWings.objects.get(pk=wings.pk)
        self.assertEqual(wings_from_db.optional_flavour, [])

    def test_update_to_empty_optional_flavour_stores_null(self):
        """Updating wings to remove all optional flavours stores NULL in the database"""
        wings = ChickenWings.objects.create(
            flavour=[ChickenWings.HOT],
            optional_flavour=[ChickenWings.JERK, ChickenWings.BACON],
        )
        wings.optional_flavour = []
        wings.save()
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT optional_flavour FROM forthewing_chickenwings WHERE id = %s",
                [wings.pk],
            )
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_update_to_empty_optional_flavour_returns_empty_list(self):
        """After updating to empty optional_flavour, loading from DB returns an empty list"""
        wings = ChickenWings.objects.create(
            flavour=[ChickenWings.HOT], optional_flavour=[ChickenWings.JERK]
        )
        wings.optional_flavour = []
        wings.save()
        wings_from_db = ChickenWings.objects.get(pk=wings.pk)
        self.assertEqual(wings_from_db.optional_flavour, [])


class DipsFormTestCase(TestCase):
    """
    This form is used to check if the field works when no option is selected
    """

    def test_valid_choices(self):
        form = DipsForm(data={"dips": [RANCH, BLUE_CHEESE]})
        self.assertTrue(form.is_valid())

    def test_no_choice_selected(self):
        form = DipsForm(data={"dips": []})
        self.assertTrue(form.is_valid())
