# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string

from django.forms import fields
from django.test import SimpleTestCase

from select_multiple_field.codecs import encode_list_to_csv
from select_multiple_field.forms import (
    DEFAULT_MAX_CHOICES_ATTR, SelectMultipleFormField)
from select_multiple_field.widgets import SelectMultipleField


class SelectMultipleFormFieldTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = tuple([(c, c) for c in string.ascii_letters])
        self.choices_list = [c[0] for c in self.choices[0:len(self.choices)]]

    def test_instantiation(self):
        ff = SelectMultipleFormField()
        self.assertIsInstance(ff, fields.Field)
        self.assertIsInstance(ff, fields.MultipleChoiceField)

    def test_widget_class(self):
        ff = SelectMultipleFormField()
        self.assertIsInstance(ff.widget, SelectMultipleField)

    def test_field_to_python_value_is_none(self):
        """Widget may return None as value for missing key in POST"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python(None), [])

    def test_field_to_python_value_is_empty_string(self):
        """Widget may return empty string as value for key in POST"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python(''), [])

    def test_field_to_python_value_is_simple_string(self):
        """Widget may return simple string as value for key in POST"""
        ff = SelectMultipleFormField()
        simple = self.choices_list[1]
        self.assertEqual(ff.to_python(simple), [simple])

    def test_field_to_python_value_is_encoded_string(self):
        """Widget may return encoded string as value for key in POST"""
        ff = SelectMultipleFormField()
        for i, v in enumerate(self.choices_list):
            subset = self.choices_list[0: i]
            encoded = encode_list_to_csv(subset)
            self.assertEqual(ff.to_python(encoded), sorted(subset))

    def test_widget_attrs_size(self):
        """Widget passed size info"""
        fake_widget = 'Fake widget'
        #
        # Case #1: Default size 4 not passed to widget
        #
        ff = SelectMultipleFormField()
        self.assertEqual(ff.size, 4)
        self.assertNotIn('size', ff.widget_attrs(fake_widget))
        #
        # Case #2: Any other size passed to widget
        #
        NON_DEFAULT_SIZE = 8
        ff = SelectMultipleFormField(size=NON_DEFAULT_SIZE)
        self.assertEqual(ff.size, NON_DEFAULT_SIZE)
        self.assertEqual(ff.widget_attrs(fake_widget).get(
            'size'), str(NON_DEFAULT_SIZE))

    def test_widget_attrs_max_choices(self):
        """Widget passed max_choices information"""
        fake_widget = 'Fake widget'
        #
        # Case #1: Optional max_choices not sent to widget
        #
        ff = SelectMultipleFormField()
        self.assertTrue(ff.max_choices is None)
        self.assertNotIn('data-max-choices', ff.widget_attrs(fake_widget))
        #
        # Case #2: When set, max_coices passed as data attribute
        #
        MAX_CHOICES = 3
        ff = SelectMultipleFormField(max_choices=MAX_CHOICES)
        self.assertEqual(ff.max_choices, MAX_CHOICES)
        self.assertEqual(ff.widget_attrs(fake_widget).get(
            DEFAULT_MAX_CHOICES_ATTR), str(MAX_CHOICES))
