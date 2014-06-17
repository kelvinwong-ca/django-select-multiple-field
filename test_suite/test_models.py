# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
import string

from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models.fields import BLANK_CHOICE_DASH, CharField, Field
from django.test import SimpleTestCase
from django.utils import six

from select_multiple_field.codecs import encode_list_to_csv
from select_multiple_field.forms import SelectMultipleFormField
from select_multiple_field.models import SelectMultipleField


class FakeCallableDefault:
    pass


class SelectMultipleFieldTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = tuple([(c, c) for c in string.ascii_letters])
        self.choices_list = [c[0] for c in self.choices[0:len(self.choices)]]
        #
        # Make some optgroup choices
        #
        optgroups = collections.defaultdict(list)
        self.num_optgroups = 5
        for n, char in enumerate(string.ascii_letters):
            optindex = n % self.num_optgroups
            optgroups[string.ascii_letters[optindex]].append((char, char))

        self.optgroup_choices = [(k, v) for k, v in optgroups.items()]

        self.optgroup_choices_list = []
        for group in self.optgroup_choices:
            self.optgroup_choices_list.extend([k for k, v in group[1]])

        self.optgroup_choices_list.sort()
        self.test_choices = [
            (self.choices, self.choices_list),
            (self.optgroup_choices, self.optgroup_choices_list)
        ]

    def test_instantiation(self):
        item = SelectMultipleField()
        self.assertIsInstance(item, Field)

    def test_instantiation_max_choices(self):
        for max_choices in range(25):
            item = SelectMultipleField(max_choices=max_choices)
            self.assertEqual(item.max_choices, max_choices)

    def test_instantiation_include_blank(self):
        item = SelectMultipleField(include_blank=False)
        self.assertFalse(item.include_blank)
        item = SelectMultipleField(include_blank=True)
        self.assertTrue(item.include_blank)

    def test_get_internal_type(self):
        item = SelectMultipleField()
        charfield = CharField()
        self.assertEquals(item.get_internal_type(),
                          charfield.get_internal_type())

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
        for choices, choices_list in self.test_choices:
            item = SelectMultipleField(choices=choices)
            self.assertTrue(item.choices)
            self.assertIsInstance(item.to_python(choices_list), list)
            self.assertEquals(item.to_python(choices_list), choices_list)

    def test_to_python_list_w_invalid_value(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertTrue(item.choices)
        invalid_list = ['InvalidChoice']
        with self.assertRaises(ValidationError) as cm:
            item.to_python(invalid_list)

        self.assertEqual(
            cm.exception.messages[0],
            (SelectMultipleField.default_error_messages['invalid_choice']
                % {'value': invalid_list[0]})
        )

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

    def test_get_choices(self):
        """Overridden get_choices suppresses blank choice tuple"""
        item = SelectMultipleField(choices=self.choices)
        choices = item.get_choices()
        self.assertIsInstance(choices, list)
        self.assertIsInstance(choices[0], tuple)
        self.assertNotIn(BLANK_CHOICE_DASH[0], choices)
        choices = item.get_choices(include_blank=False)
        self.assertIsInstance(choices, list)
        self.assertIsInstance(choices[0], tuple)
        self.assertNotIn(BLANK_CHOICE_DASH[0], choices)

    def test_get_choices_w_blank_choice(self):
        """Overridden get_choices suppresses blank choice tuple"""
        item = SelectMultipleField(choices=self.choices)
        choices = item.get_choices(include_blank=True)
        self.assertIsInstance(choices, list)
        self.assertIsInstance(choices[0], tuple)
        self.assertIn(BLANK_CHOICE_DASH[0], choices)

    def test_get_choices_include_blank(self):
        """
        Explicit include_blank value is honored, ignoring passed parameters
        """
        item = SelectMultipleField(choices=self.choices, include_blank=True)
        choices = item.get_choices()
        self.assertIsInstance(choices, list)
        self.assertIsInstance(choices[0], tuple)
        self.assertIn(BLANK_CHOICE_DASH[0], choices)
        choices = item.get_choices(include_blank=False)
        self.assertIsInstance(choices, list)
        self.assertIsInstance(choices[0], tuple)
        self.assertIn(BLANK_CHOICE_DASH[0], choices)
        item = SelectMultipleField(choices=self.choices, include_blank=False)
        choices = item.get_choices()
        self.assertIsInstance(choices, list)
        self.assertIsInstance(choices[0], tuple)
        self.assertNotIn(BLANK_CHOICE_DASH[0], choices)
        choices = item.get_choices(include_blank=True)
        self.assertIsInstance(choices, list)
        self.assertIsInstance(choices[0], tuple)
        self.assertNotIn(BLANK_CHOICE_DASH[0], choices)

    def test_validate_valid_choices(self):
        for choices in self.test_choices:
            item = SelectMultipleField(choices=choices[0])
            item.editable = True
            instance = "Fake Unused Instance"
            for i, v in enumerate(choices[1]):
                subset = self.choices_list[0: i + 1]
                self.assertIs(item.validate(subset, instance), None)

    def test_validate_not_editable(self):
        item = SelectMultipleField()
        item.editable = False
        value = "Any Value"
        instance = "Fake Unused Instance"
        self.assertIs(item.validate(value, instance), None)

    def test_validate_invalid_choice(self):
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        value = ["Invalid Choice"]
        instance = "Fake Unused Instance"
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate(value, instance))

        self.assertEqual(
            cm.exception.messages[0],
            (SelectMultipleField.default_error_messages['invalid_choice']
                % {'value': value})
        )

    def test_validate_invalid_string(self):
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        value = "Invalid Choice"
        instance = "Fake Unused Instance"
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate(value, instance))

        self.assertEqual(
            cm.exception.messages[0],
            (SelectMultipleField.default_error_messages['invalid_choice']
                % {'value': value})
        )

    def test_validate_not_null(self):
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        item.null = False
        value = None
        instance = "Fake Unused Instance"
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate(value, instance))

        self.assertEqual(
            cm.exception.messages[0],
            SelectMultipleField.default_error_messages['null']
        )

    def test_validate_blank(self):
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        item.blank = True
        value = ['']
        instance = "Fake Unused Instance"
        self.assertIs(item.validate(value, instance), None)

    def test_validate_not_blank(self):
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        item.blank = False
        value = []
        instance = "Fake Unused Instance"
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate(value, instance))

        self.assertEqual(
            cm.exception.messages[0],
            SelectMultipleField.default_error_messages['blank']
        )

    def test_validate_options_list(self):
        item = SelectMultipleField(choices=self.choices)
        value = self.choices_list
        self.assertIs(item.validate_options_list(value), None)

    def test_validate_options_list_raises_validationerror(self):
        item = SelectMultipleField(choices=self.choices)
        value = ['InvalidChoice']
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate_options_list(value))

        self.assertEqual(
            cm.exception.messages[0],
            (SelectMultipleField.default_error_messages['invalid_choice']
                % {'value': value[0]})
        )

    def test_validate_option_choice_true(self):
        item = SelectMultipleField(choices=self.choices)
        for n in range(len(self.choices_list) - 1):
            self.assertTrue(item.validate_option(self.choices_list[n]))

    def test_validate_option_choice_false(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertFalse(item.validate_option("InvalidChoice"))

    def test_validate_option_choice_blank_values(self):
        item = SelectMultipleField(choices=self.choices)
        item.blank = True
        self.assertTrue(item.blank)
        for value in validators.EMPTY_VALUES:
            self.assertTrue(item.validate_option(value))

    def test_get_choices_keys(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertEqual(item.get_choices_keys(), self.choices_list)

    def test_get_choices_keys_optgroup(self):
        item = SelectMultipleField(choices=self.optgroup_choices)
        choices = item.get_choices_keys()
        self.assertEqual(len(choices), len(self.optgroup_choices_list))
        for n in choices:
            self.assertIn(n, self.optgroup_choices_list)

    def test_formfield(self):
        item = SelectMultipleField()
        form = item.formfield()
        self.assertIsInstance(form, SelectMultipleFormField)

    def test_formfield_default_is_callable(self):
        item = SelectMultipleField(default=FakeCallableDefault)
        form = item.formfield()
        self.assertIsInstance(form, SelectMultipleFormField)
        self.assertTrue(item.has_default())
        self.assertTrue(callable(form.initial))
        self.assertIs(form.initial, FakeCallableDefault)

    def test_formfield_default_string(self):
        string_default = "String As Default"
        item = SelectMultipleField(default=string_default)
        form = item.formfield()
        self.assertIsInstance(form, SelectMultipleFormField)
        self.assertTrue(item.has_default())
        self.assertEqual(item.get_default(), string_default)
        self.assertEqual(form.initial, string_default)

    def test_formfield_no_empty_value_by_default(self):
        """
        Formfield returns no empty value by default
        """
        item = SelectMultipleField(choices=self.choices)
        form = item.formfield()
        self.assertIsInstance(form, SelectMultipleFormField)
        self.assertFalse(item.has_default())
        self.assertEqual(form.coerce, item.to_python)
        self.assertFalse(item.blank)
        self.assertTrue(form.required)
        self.assertFalse(item.null)
        self.assertEqual(form.empty_value, [])
        self.assertNotIn(BLANK_CHOICE_DASH[0], form.choices)

    def test_formfield_empty_value_w_blank(self):
        """
        Formfield can return empty value, set ModelField.blank to True
        """
        item = SelectMultipleField(choices=self.choices, blank=True)
        form = item.formfield()
        self.assertIsInstance(form, SelectMultipleFormField)
        self.assertEqual(form.coerce, item.to_python)
        self.assertTrue(item.blank)
        self.assertFalse(form.required)
        self.assertFalse(item.null)
        self.assertEqual(form.empty_value, [])
        self.assertIn(BLANK_CHOICE_DASH[0], form.choices)
