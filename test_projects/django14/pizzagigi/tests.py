# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.test import TestCase
#from django.test.client import RequestFactory

from .models import Pizza


class PizzaListViewTestCase(TestCase):

    def test_view(self):
        response = self.client.get(reverse('pizza:list'))
        self.assertEqual(response.status_code, 200)


class PizzaCreateViewTestCase(TestCase):

    def test_view(self):
        response = self.client.get(reverse('pizza:create'))
        self.assertEqual(response.status_code, 200)
