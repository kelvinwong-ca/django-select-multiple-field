# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import SimpleTestCase, TestCase
from django.utils.datastructures import MultiValueDict
from django.utils.http import urlencode

from .models import Pizza, show_topping


class PizzaListViewTestCase(TestCase):

    def test_no_pizzas(self):
        p = Pizza.objects.all()
        self.assertEqual(len(p), 0, 'Test requires no pizzas')
        response = self.client.get(reverse('pizza:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('No pizzas found' in response.content.decode('utf-8'))

    def test_many_pizzas(self):
        NUM_PIZZAS = 30
        pizzas = []
        for n in range(NUM_PIZZAS):
            p = Pizza.objects.create(toppings=[Pizza.PEPPERONI])
            pizzas.append(p)

        self.assertEqual(len(pizzas), NUM_PIZZAS, 'Test requires pizzas')
        response = self.client.get(reverse('pizza:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            show_topping(Pizza.PEPPERONI) in response.content.decode('utf-8'))


class PizzaCreateViewTestCase(TestCase):

    def test_view(self):
        response = self.client.get(reverse('pizza:create'))
        self.assertEqual(response.status_code, 200)

    def test_creation_single(self):
        data = {
            'toppings': [Pizza.BLACK_OLIVES]
        }
        response = self.client.post(
            reverse('pizza:create'),
            urlencode(MultiValueDict(data), doseq=True),
            content_type='application/x-www-form-urlencoded'
            )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            'http://testserver' + reverse('pizza:created'))
        p = Pizza.objects.all()[0]
        self.assertIn(Pizza.BLACK_OLIVES, p.toppings)

    def test_creation_multiple(self):
        data = {
            'toppings': [Pizza.MOZZARELLA, Pizza.PANCETTA]
        }
        response = self.client.post(
            reverse('pizza:create'),
            urlencode(MultiValueDict(data), doseq=True),
            content_type='application/x-www-form-urlencoded'
            )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            'http://testserver' + reverse('pizza:created'))
        p = Pizza.objects.all()[0]
        self.assertIn(Pizza.MOZZARELLA, p.toppings)
        self.assertIn(Pizza.PANCETTA, p.toppings)


class PizzaDetailViewTestCase(TestCase):

    def setUp(self):
        self.pizza = Pizza(toppings=[Pizza.EGG])
        self.pizza.save()

    def test_view(self):
        response = self.client.get(
            reverse('pizza:detail', args=[self.pizza.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.pizza)


class PizzaUpdateViewTestCase(TestCase):

    def setUp(self):
        self.pizza = Pizza(toppings=[Pizza.MUSHROOMS, Pizza.TOMATO])
        self.pizza.save()

    def test_change_toppings(self):
        data = {
            'toppings': [Pizza.CHEDDAR_CHEESE, Pizza.MUSHROOMS]
        }
        response = self.client.post(
            reverse('pizza:update', args=[self.pizza.id]),
            urlencode(MultiValueDict(data), doseq=True),
            content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            'http://testserver' + reverse('pizza:updated'))
        p = Pizza.objects.all()[0]
        self.assertTrue(Pizza.CHEDDAR_CHEESE in p.toppings)
        self.assertTrue(Pizza.MUSHROOMS in p.toppings)
        self.assertFalse(Pizza.TOMATO in p.toppings)


class PizzaDeleteViewTestCase(TestCase):

    def setUp(self):
        self.pizza = Pizza(toppings=[Pizza.PROSCIUTTO_CRUDO])
        self.pizza.save()

    def test_delete_pizza(self):
        response = self.client.post(
            reverse('pizza:delete', args=[self.pizza.id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            'http://testserver' + reverse('pizza:deleted'))
        pl = Pizza.objects.all()
        self.assertEqual(len(pl), 0)


class PizzaModelTestCase(SimpleTestCase):

    def test_show_topping(self):
        for k, v in Pizza.TOPPING_CHOICES:
            topping_name = show_topping(k)
            self.assertEqual(topping_name, v)
