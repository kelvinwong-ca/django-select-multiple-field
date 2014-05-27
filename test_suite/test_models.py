#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import string

from django.db.models.fields import Field
from django.test import SimpleTestCase
from django.utils import six
#from django.utils.six.moves import xrange

from select_multiple_field.models import SelectMultipleField


class SelectMultipleFieldTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = tuple([(c, c) for c in string.ascii_letters])
        self.choices_list = [c[0] for c in self.choices[0:len(self.choices)]]

    def test_instantiation(self):
        item = SelectMultipleField()
        self.assertIsInstance(item, Field)

    def test_get_prep_value_list(self):
        item = SelectMultipleField()
        self.assertIsInstance(
            item.get_prep_value(self.choices_list), six.string_types)
