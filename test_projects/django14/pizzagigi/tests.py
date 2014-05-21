# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import SimpleTestCase, TestCase

from .models import Pizza, show_topping


class PizzaListViewTestCase(TestCase):

    def test_view(self):
        response = self.client.get(reverse('pizza:list'))
        self.assertEqual(response.status_code, 200)


class PizzaCreateViewTestCase(TestCase):

    def test_view(self):
        response = self.client.get(reverse('pizza:create'))
        self.assertEqual(response.status_code, 200)

    def test_creation(self):
        data = {
            'toppings': [Pizza.MOZZARELLA, Pizza.PEPPERONI]
        }
        response = self.client.post(reverse('pizza:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            'http://testserver' + reverse('pizza:created'))
        p = Pizza.objects.all()[0]
        self.assertTrue(Pizza.MOZZARELLA in p.toppings)
        self.assertTrue(Pizza.PEPPERONI in p.toppings)


class PizzaDetailViewTestCase(TestCase):

    def setUp(self):
        self.pizza = Pizza(toppings=[Pizza.PEPPERONI])
        self.pizza.save()

    def test_view(self):
        response = self.client.get(
            reverse('pizza:detail', args=[self.pizza.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.pizza)


class PizzaUpdateViewTestCase(TestCase):

    def setUp(self):
        self.pizza = Pizza(toppings=[Pizza.MOZZARELLA, Pizza.PEPPERONI])
        self.pizza.save()

    def test_change_toppings(self):
        data = {
            'toppings': [Pizza.CHEDDAR_CHEESE, Pizza.MOZZARELLA]
        }
        response = self.client.post(
            reverse('pizza:update', args=[self.pizza.id]), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            'http://testserver' + reverse('pizza:updated'))
        p = Pizza.objects.all()[0]
        self.assertTrue(Pizza.CHEDDAR_CHEESE in p.toppings)
        self.assertTrue(Pizza.MOZZARELLA in p.toppings)
        self.assertFalse(Pizza.PEPPERONI in p.toppings)


class PizzaDeleteViewTestCase(TestCase):

    def setUp(self):
        self.pizza = Pizza(toppings=[Pizza.PEPPERONI])
        self.pizza.save()

    def test_delete_pizza(self):
        response = self.client.post(
            reverse('pizza:delete', args=[self.pizza.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            'http://testserver' + reverse('pizza:deleted'))
        pl = Pizza.objects.all()
        self.assertEqual(len(pl), 0)


class PizzaModelTestCase(SimpleTestCase):

    def test_show_topping(self):
        for k, v in Pizza.TOPPING_CHOICES:
            topping_name = show_topping(k)
            self.assertEqual(topping_name, v)
