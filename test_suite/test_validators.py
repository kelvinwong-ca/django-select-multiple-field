# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import string

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from select_multiple_field.codecs import encode_list_to_csv
from select_multiple_field.models import SelectMultipleField
from select_multiple_field.validators import (
    MaxChoicesValidator, MaxLengthValidator)


class SelectMultipleFieldValidatorsTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = tuple([(c, c) for c in string.ascii_letters])
        self.choices_list = [c[0] for c in self.choices[0:len(self.choices)]]

    def test_max_choices_single(self):
        item = SelectMultipleField(
            choices=self.choices, max_length=254, max_choices=1)
        self.assertEqual(item.max_choices, 1)
        self.assertIsInstance(item.validators[1], MaxChoicesValidator)
        self.assertIs(item.run_validators(self.choices_list[0:1]), None)

    def test_max_choices_many(self):
        for n in range(2, len(self.choices_list)):
            many_choices = self.choices_list[0:n]
            many_choices_len = len(many_choices)
            item = SelectMultipleField(
                choices=self.choices,
                max_length=254,
                max_choices=many_choices_len)
            self.assertEqual(item.max_choices, many_choices_len)
            self.assertIsInstance(item.validators[1], MaxChoicesValidator)
            self.assertIs(item.run_validators(many_choices), None)

    def test_max_choices_validationerror_single(self):
        item = SelectMultipleField(
            choices=self.choices, max_length=10, max_choices=1)
        self.assertEqual(item.max_choices, 1)
        self.assertIsInstance(item.validators[1], MaxChoicesValidator)
        two_choices = self.choices_list[0:2]
        with self.assertRaises(ValidationError) as cm:
            item.run_validators(value=two_choices)

        self.assertEqual(
            cm.exception.messages[0],
            MaxChoicesValidator.message % {
                'limit_value': 1,
                'show_value': len(two_choices)
            }
        )

    def test_max_choices_validationerror_many(self):
        for n in range(3, len(self.choices_list)):
            test_max_choices = n - 1  # One less than encoded list len
            item = SelectMultipleField(
                choices=self.choices,
                max_length=254,
                max_choices=test_max_choices)
            self.assertEqual(item.max_choices, test_max_choices)
            self.assertIsInstance(item.validators[1], MaxChoicesValidator)
            many_choices = self.choices_list[0:n]
            many_choices_len = len(many_choices)
            self.assertTrue(many_choices_len > test_max_choices)
            with self.assertRaises(ValidationError) as cm:
                item.run_validators(value=many_choices)

            self.assertEqual(
                cm.exception.messages[0],
                MaxChoicesValidator.message % {
                    'limit_value': item.max_choices,
                    'show_value': many_choices_len}
            )

    def test_max_length_single(self):
        item = SelectMultipleField(choices=self.choices, max_length=1)
        self.assertEqual(item.max_length, 1)
        self.assertIsInstance(item.validators[0], MaxLengthValidator)
        choice = self.choices_list[0:1]
        self.assertIs(item.run_validators(value=choice), None)

    def test_max_length_many(self):
        for n in range(2, len(self.choices_list)):
            many_choices = self.choices_list[0:n]
            encoded_choices_len = len(encode_list_to_csv(many_choices))
            item = SelectMultipleField(
                choices=self.choices, max_length=encoded_choices_len)
            self.assertEqual(item.max_length, encoded_choices_len)
            self.assertIsInstance(item.validators[0], MaxLengthValidator)
            self.assertIs(item.run_validators(value=many_choices), None)

    def test_max_length_validationerror_single(self):
        item = SelectMultipleField(choices=self.choices, max_length=1)
        self.assertEqual(item.max_length, 1)
        self.assertIsInstance(item.validators[0], MaxLengthValidator)
        two_choices = self.choices_list[0:2]
        with self.assertRaises(ValidationError) as cm:
            item.run_validators(value=two_choices)

        self.assertEqual(
            cm.exception.messages[0],
            MaxLengthValidator.message % {'limit_value': 1, 'show_value': 3}
        )

    def test_max_length_validationerror_many(self):
        for n in range(2, len(self.choices_list)):
            test_max_length = 2 * n - 2  # One less than encoded list len
            item = SelectMultipleField(
                choices=self.choices, max_length=test_max_length)
            self.assertEqual(item.max_length, test_max_length)
            self.assertIsInstance(item.validators[0], MaxLengthValidator)
            many_choices = self.choices_list[0:n]
            many_choices_len = len(encode_list_to_csv(many_choices))
            self.assertTrue(many_choices_len > test_max_length)
            with self.assertRaises(ValidationError) as cm:
                item.run_validators(value=many_choices)

            self.assertEqual(
                cm.exception.messages[0],
                MaxLengthValidator.message % {
                    'limit_value': item.max_length,
                    'show_value': many_choices_len}
            )
