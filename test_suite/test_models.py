# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string

from django.core.exceptions import ValidationError
from django.db.models.fields import Field
from django.test import SimpleTestCase
from django.utils import six

from select_multiple_field.codecs import encode_list_to_csv
from select_multiple_field.models import SelectMultipleField


class SelectMultipleFieldTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = tuple([(c, c) for c in string.ascii_letters])
        self.choices_list = [c[0] for c in self.choices[0:len(self.choices)]]

    def test_instantiation(self):
        item = SelectMultipleField()
        self.assertIsInstance(item, Field)

    def test_get_prep_value_none(self):
        """None stored as NULL in db"""
        item = SelectMultipleField()
        self.assertIs(item.get_prep_value(None), None)

    def test_get_prep_value_empty_list(self):
        """No choice stored as empty string"""
        item = SelectMultipleField()
        self.assertIsInstance(
            item.get_prep_value([]), six.string_types)
        self.assertEquals(
            item.get_prep_value([]), '')

    def test_get_prep_value_list(self):
        item = SelectMultipleField()
        self.assertIsInstance(
            item.get_prep_value(self.choices_list), six.string_types)

    def test_to_python_none(self):
        item = SelectMultipleField()
        self.assertIs(item.to_python(None), None)

    def test_to_python_empty_list(self):
        item = SelectMultipleField()
        self.assertIsInstance(item.to_python([]), list)
        self.assertEquals(item.to_python([]), [])

    def test_to_python_list(self):
        item = SelectMultipleField()
        self.assertIsInstance(item.to_python(self.choices_list), list)
        self.assertEquals(item.to_python(self.choices_list), self.choices_list)

    def test_to_python_empty_string(self):
        item = SelectMultipleField()
        self.assertIsInstance(
            item.to_python(''), list)
        self.assertEquals(
            item.to_python(''), [])

    def test_to_python_single_string(self):
        item = SelectMultipleField()
        single = self.choices_list[3]
        self.assertIsInstance(
            item.to_python(single), list)
        self.assertEquals(
            item.to_python(single), [single])

    def test_to_python_string(self):
        item = SelectMultipleField()
        for i, v in enumerate(self.choices_list):
            subset = self.choices_list[0: i]
            encoded = encode_list_to_csv(subset)
            self.assertIsInstance(item.to_python(encoded), list)
            self.assertEqual(item.to_python(encoded), sorted(subset))

    def test_to_python_invalid_type(self):
        item = SelectMultipleField()
        invalid_type = True
        with self.assertRaises(ValidationError) as cm:
            item.to_python(invalid_type)

        self.assertEqual(
            cm.exception.messages[0],
            (SelectMultipleField.default_error_messages['invalid_type']
                % {'value': type(invalid_type)}))
