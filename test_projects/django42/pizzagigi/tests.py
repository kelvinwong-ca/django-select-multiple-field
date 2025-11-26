import json

from django.core import serializers
from django.db import connection
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode

from test_projects.asserts import safe_assert_redirects

from .models import Pizza, show_dip, show_topping


class PizzaListViewTestCase(TestCase):

    def test_no_pizzas(self):
        p = Pizza.objects.all()
        self.assertEqual(len(p), 0, "Test requires no pizzas")
        response = self.client.get(reverse("pizza:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("No pizzas found" in response.content.decode("utf-8"))

    def test_many_pizzas(self):
        NUM_PIZZAS = 30
        pizzas = []
        for n in range(NUM_PIZZAS):
            p = Pizza.objects.create(toppings=[Pizza.PEPPERONI])
            pizzas.append(p)

        self.assertEqual(len(pizzas), NUM_PIZZAS, "Test requires pizzas")
        response = self.client.get(reverse("pizza:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            show_topping(Pizza.PEPPERONI) in response.content.decode("utf-8")
        )


class PizzaCreateViewTestCase(TestCase):

    def test_view(self):
        response = self.client.get(reverse("pizza:create"))
        self.assertEqual(response.status_code, 200)

    def test_creation_single(self):
        data = {"toppings": [Pizza.BLACK_OLIVES]}
        response = self.client.post(
            reverse("pizza:create"),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )

        self.assertEqual(response.status_code, 302)
        safe_assert_redirects(self, response, reverse("pizza:created"))
        p = Pizza.objects.all()[0]
        self.assertIn(Pizza.BLACK_OLIVES, p.toppings)

    def test_creation_multiple(self):
        data = {"toppings": [Pizza.MOZZARELLA, Pizza.PANCETTA]}
        response = self.client.post(
            reverse("pizza:create"),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 302)
        safe_assert_redirects(self, response, reverse("pizza:created"))
        p = Pizza.objects.all()[0]
        self.assertIn(Pizza.MOZZARELLA, p.toppings)
        self.assertIn(Pizza.PANCETTA, p.toppings)

    def test_creation_no_toppings(self):
        """
        If a placeholder empty value is sent, the toppings list should be empty.
        """
        data = {"toppings": [Pizza.MOZZARELLA], "dips": [""]}
        response = self.client.post(
            reverse("pizza:create"),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )

        safe_assert_redirects(self, response, reverse("pizza:created"))
        p = Pizza.objects.all()[0]
        self.assertListEqual(p.dips, [])


class PizzaDetailViewTestCase(TestCase):

    def setUp(self):
        self.pizza = Pizza(toppings=[Pizza.EGG])
        self.pizza.save()

    def test_view(self):
        response = self.client.get(reverse("pizza:detail", args=[self.pizza.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], self.pizza)


class PizzaUpdateViewTestCase(TestCase):

    def setUp(self):
        self.pizza = Pizza(toppings=[Pizza.MUSHROOMS, Pizza.TOMATO])
        self.pizza.save()

    def test_change_toppings(self):
        data = {"toppings": [Pizza.CHEDDAR_CHEESE, Pizza.MUSHROOMS]}
        response = self.client.post(
            reverse("pizza:update", args=[self.pizza.id]),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 302)
        safe_assert_redirects(self, response, reverse("pizza:updated"))

        p = Pizza.objects.all()[0]
        self.assertTrue(Pizza.CHEDDAR_CHEESE in p.toppings)
        self.assertTrue(Pizza.MUSHROOMS in p.toppings)
        self.assertFalse(Pizza.TOMATO in p.toppings)


class PizzaDeleteViewTestCase(TestCase):

    def setUp(self):
        self.pizza = Pizza(toppings=[Pizza.PROSCIUTTO_CRUDO])
        self.pizza.save()

    def test_delete_pizza(self):
        response = self.client.post(reverse("pizza:delete", args=[self.pizza.id]))
        self.assertEqual(response.status_code, 302)
        safe_assert_redirects(self, response, reverse("pizza:deleted"))
        pl = Pizza.objects.all()
        self.assertEqual(len(pl), 0)


class PizzaModelTestCase(TestCase):

    def test_show_topping(self):
        for k, v in Pizza.TOPPING_CHOICES:
            topping_name = show_topping(k)
            self.assertEqual(topping_name, v)

    def test_show_topping_unknown_key(self):
        result = show_topping("unknown")
        self.assertEqual(result, "unknown")

    def test_show_dip_unknown_key(self):
        result = show_dip("unknown")
        self.assertEqual(result, "unknown")

    def test_value_converted_to_list_from_db(self):
        pizza = Pizza.objects.create(toppings=[Pizza.PEPPERONI])
        pizza_from_db = Pizza.objects.get(pk=pizza.pk)
        self.assertEqual(pizza_from_db.toppings, [Pizza.PEPPERONI])


class PizzaNullDipsTestCase(TestCase):
    """Tests for null=True storage behavior on the dips field"""

    def test_create_with_no_dips_stores_null(self):
        """Creating a pizza without dips stores NULL in the database"""
        pizza = Pizza.objects.create(toppings=[Pizza.PEPPERONI])
        with connection.cursor() as cursor:
            cursor.execute("SELECT dips FROM pizzagigi_pizza WHERE id = %s", [pizza.pk])
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_create_with_empty_dips_stores_null(self):
        """Creating a pizza with empty dips list stores NULL in the database"""
        pizza = Pizza.objects.create(toppings=[Pizza.PEPPERONI], dips=[])
        with connection.cursor() as cursor:
            cursor.execute("SELECT dips FROM pizzagigi_pizza WHERE id = %s", [pizza.pk])
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_create_with_dips_stores_string(self):
        """Creating a pizza with dips stores an encoded string in the database"""
        pizza = Pizza.objects.create(toppings=[Pizza.PEPPERONI], dips=[Pizza.RANCH])
        with connection.cursor() as cursor:
            cursor.execute("SELECT dips FROM pizzagigi_pizza WHERE id = %s", [pizza.pk])
            row = cursor.fetchone()
        self.assertIsInstance(row[0], str)

    def test_load_null_dips_returns_empty_list(self):
        """Loading a pizza with NULL dips from the database returns an empty list"""
        pizza = Pizza.objects.create(toppings=[Pizza.PEPPERONI])
        pizza_from_db = Pizza.objects.get(pk=pizza.pk)
        self.assertEqual(pizza_from_db.dips, [])

    def test_update_to_empty_dips_stores_null(self):
        """Updating a pizza to remove all dips stores NULL in the database"""
        pizza = Pizza.objects.create(
            toppings=[Pizza.PEPPERONI], dips=[Pizza.RANCH, Pizza.BLUE_CHEESE]
        )
        pizza.dips = []
        pizza.save()
        with connection.cursor() as cursor:
            cursor.execute("SELECT dips FROM pizzagigi_pizza WHERE id = %s", [pizza.pk])
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_update_to_empty_dips_returns_empty_list(self):
        """After updating to empty dips, loading from DB returns an empty list"""
        pizza = Pizza.objects.create(toppings=[Pizza.PEPPERONI], dips=[Pizza.RANCH])
        pizza.dips = []
        pizza.save()
        pizza_from_db = Pizza.objects.get(pk=pizza.pk)
        self.assertEqual(pizza_from_db.dips, [])

    def test_create_view_no_dips_stores_null(self):
        """POST to create view with no dips field stores NULL in database"""
        data = {"toppings": [Pizza.PEPPERONI]}
        response = self.client.post(
            reverse("pizza:create"),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 302)
        pizza = Pizza.objects.all()[0]
        with connection.cursor() as cursor:
            cursor.execute("SELECT dips FROM pizzagigi_pizza WHERE id = %s", [pizza.pk])
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_create_view_empty_dips_stores_null(self):
        """POST to create view with empty dips stores NULL in database"""
        data = {"toppings": [Pizza.PEPPERONI], "dips": [""]}
        response = self.client.post(
            reverse("pizza:create"),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 302)
        pizza = Pizza.objects.all()[0]
        with connection.cursor() as cursor:
            cursor.execute("SELECT dips FROM pizzagigi_pizza WHERE id = %s", [pizza.pk])
            row = cursor.fetchone()
        self.assertIsNone(row[0])

    def test_update_view_clear_dips_stores_null(self):
        """POST to update view clearing dips stores NULL in database"""
        pizza = Pizza.objects.create(toppings=[Pizza.PEPPERONI], dips=[Pizza.RANCH])
        data = {"toppings": [Pizza.PEPPERONI], "dips": [""]}
        response = self.client.post(
            reverse("pizza:update", args=[pizza.pk]),
            urlencode(MultiValueDict(data), doseq=True),
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 302)
        pizza_from_db = Pizza.objects.get(pk=pizza.pk)
        with connection.cursor() as cursor:
            cursor.execute("SELECT dips FROM pizzagigi_pizza WHERE id = %s", [pizza.pk])
            row = cursor.fetchone()
        self.assertIsNone(row[0])
        self.assertEqual(pizza_from_db.dips, [])


class PizzaCozyTestCase(TestCase):
    """Serialzer tests for dumpdata operations"""

    def setUp(self):
        self.toppings_1 = [
            Pizza.ANCHOVIES,
            Pizza.BLACK_OLIVES,
            Pizza.CHEDDAR_CHEESE,
        ]
        self.pizza_1 = Pizza.objects.create(toppings=self.toppings_1)
        self.toppings_2 = [
            Pizza.TOMATO,
            Pizza.MOZZARELLA,
        ]
        self.pizza_2 = Pizza.objects.create(toppings=self.toppings_2)

    def test_dumpdata_dumps_json(self):
        """JSON can handle a native list type not only strings"""
        q = Pizza.objects.all()
        output = serializers.serialize("json", q)

        js = json.loads(output)

        self.assertTrue(isinstance(js, list))
        ingredients = []
        for i, __ in enumerate(js):
            ingredients.extend(js[i]["fields"]["toppings"])

        for topping in list(self.toppings_1 + self.toppings_2):
            self.assertIn(topping, ingredients)
