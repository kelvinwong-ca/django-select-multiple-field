import string
from unittest.mock import patch

from django.forms import fields
from django.test import SimpleTestCase

from select_multiple_field.codecs import encode_list_to_csv
from select_multiple_field.forms import (
    DEFAULT_MAX_CHOICES_ATTR,
    SelectMultipleFormField,
)
from select_multiple_field.widgets import SelectMultipleWidget


class SelectMultipleFormFieldTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = tuple([(c, c) for c in string.ascii_letters])
        self.choices_list = [c[0] for c in self.choices[0 : len(self.choices)]]

    def test_instantiation(self):
        ff = SelectMultipleFormField()
        self.assertIsInstance(ff, fields.Field)
        self.assertIsInstance(ff, fields.MultipleChoiceField)

    def test_widget_class(self):
        ff = SelectMultipleFormField()
        self.assertIsInstance(ff.widget, SelectMultipleWidget)

    def test_field_to_python_value_is_none(self):
        """Widget may return None as value for missing key in POST"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python(None), [])

    def test_field_to_python_value_is_empty_string(self):
        """Widget may return empty string as value for key in POST"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python(""), [])

    def test_field_to_python_value_is_empty_list(self):
        """Widget may return empty list as value for key in POST"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python([]), [])

    def test_field_to_python_value_is_simple_string(self):
        """Widget may return simple string as value for key in POST"""
        ff = SelectMultipleFormField()
        simple = self.choices_list[1]
        self.assertEqual(ff.to_python(simple), [simple])

    def test_field_to_python_value_is_encoded_string(self):
        """Widget may return encoded string as value for key in POST"""
        ff = SelectMultipleFormField()
        for i, v in enumerate(self.choices_list):
            subset = self.choices_list[0:i]
            encoded = encode_list_to_csv(subset)
            self.assertEqual(ff.to_python(encoded), subset)

    def test_field_to_python_value_is_list_with_empty_string(self):
        """Widget may return a list containing empty string when no choice selected"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python([""]), [])

    def test_field_to_python_value_is_list_with_multiple_empty_strings(self):
        """Widget may return a list containing multiple empty strings when no choice selected"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python(["", ""]), [])

    def test_field_to_python_empty_list_with_null_empty_value(self):
        """When empty_value=None (null=True), list with empty strings returns empty list"""
        ff = SelectMultipleFormField(empty_value=None)
        # to_python returns [] since iter(None) raises TypeError
        self.assertEqual(ff.to_python([""]), [])

    def test_field_to_python_empty_value_not_shared_between_instances(self):
        """to_python() must return a fresh list, not a shared mutable empty_value"""
        ff = SelectMultipleFormField()

        # Multiple calls to to_python on the same instance
        empty1 = ff.to_python([])
        empty2 = ff.to_python([])

        # They should be equal but not the same object
        self.assertEqual(empty1, empty2)
        self.assertIsNot(empty1, empty2)

        # Mutating one must not affect the other
        empty1.append("mutated")
        self.assertNotIn("mutated", empty2)
        self.assertEqual(empty2, [])

    def test_field_to_python_empty_value_not_shared_across_instances(self):
        """Different form instances must not share empty_value"""
        ff1 = SelectMultipleFormField()
        ff2 = SelectMultipleFormField()

        empty1 = ff1.to_python([])
        empty2 = ff2.to_python([])

        # They should be equal but not the same object
        self.assertEqual(empty1, empty2)
        self.assertIsNot(empty1, empty2)

        # Mutating one must not affect the other
        empty1.append("mutated")
        self.assertNotIn("mutated", empty2)
        self.assertEqual(empty2, [])

    def test_field_to_python_list_with_mixed_empty_and_nonempty(self):
        """List with both empty and non-empty values falls through to list(value)"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python(["a", ""]), ["a", ""])
        self.assertEqual(ff.to_python(["", "b"]), ["", "b"])
        self.assertEqual(ff.to_python(["a", "", "c"]), ["a", "", "c"])

    def test_field_to_python_tuple_input(self):
        """Tuple input is coerced to list"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python(("a", "b")), ["a", "b"])

    def test_field_to_python_empty_tuple(self):
        """Empty tuple returns empty list"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python(()), [])

    def test_field_to_python_set_input(self):
        """Set input falls through to list(value)"""
        ff = SelectMultipleFormField()
        self.assertEqual(ff.to_python({"a"}), ["a"])

    def test_field_to_python_generator_input(self):
        """Generator input falls through to list(value)"""
        ff = SelectMultipleFormField()
        result = ff.to_python(x for x in ["a", "b"])
        self.assertEqual(result, ["a", "b"])

    def test_field_to_python_empty_value_tuple_is_iterable(self):
        """When empty_value=() (tuple), iter(empty_value) succeeds and returns list copy"""
        ff = SelectMultipleFormField(empty_value=())
        self.assertEqual(ff.to_python([""]), [])

    def test_field_to_python_empty_value_none_with_none_input(self):
        """When empty_value=None and value is None, elif branch TypeError returns []"""
        ff = SelectMultipleFormField(empty_value=None)
        self.assertEqual(ff.to_python(None), [])

    def test_field_to_python_empty_value_none_with_empty_string(self):
        """When empty_value=None and value is empty string, elif branch TypeError returns []"""
        ff = SelectMultipleFormField(empty_value=None)
        self.assertEqual(ff.to_python(""), [])

    def test_get_choices(self):
        """get_choices() returns a list of choices"""
        ff = SelectMultipleFormField(choices=self.choices)
        choices = ff.get_choices()
        self.assertIsInstance(choices, list)
        self.assertEqual(len(choices), len(self.choices))

    def test_get_choices_stores_include_blank(self):
        """
        include_blank kwarg is stored as instance attribute

        Using this param causes a deprecation warning.
        """
        ff = SelectMultipleFormField(choices=self.choices, include_blank=True)
        self.assertTrue(ff.include_blank)

    def test_get_choices_include_blank_default(self):
        """
        include_blank defaults to False when not provided

        Using this param causes a deprecation warning.
        """
        ff = SelectMultipleFormField(choices=self.choices)
        choices = ff.get_choices()
        self.assertNotIn(("", "---------"), choices)

    def test_widget_attrs_size(self):
        """Widget passed size info"""
        fake_widget = "Fake widget"
        #
        # Case #1: Default size 4 not passed to widget
        #
        ff = SelectMultipleFormField()
        self.assertEqual(ff.size, 4)
        self.assertNotIn("size", ff.widget_attrs(fake_widget))
        #
        # Case #2: Any other size passed to widget
        #
        NON_DEFAULT_SIZE = 8
        ff = SelectMultipleFormField(size=NON_DEFAULT_SIZE)
        self.assertEqual(ff.size, NON_DEFAULT_SIZE)
        self.assertEqual(
            ff.widget_attrs(fake_widget).get("size"), str(NON_DEFAULT_SIZE)
        )

    def test_widget_attrs_max_choices(self):
        """Widget passed max_choices information"""
        fake_widget = "Fake widget"
        #
        # Case #1: Optional max_choices not sent to widget
        #
        ff = SelectMultipleFormField()
        self.assertTrue(ff.max_choices is None)
        self.assertNotIn("data-max-choices", ff.widget_attrs(fake_widget))
        #
        # Case #2: When set, max_choices passed as data attribute
        #
        MAX_CHOICES = 3
        ff = SelectMultipleFormField(max_choices=MAX_CHOICES)
        self.assertEqual(ff.max_choices, MAX_CHOICES)
        self.assertEqual(
            ff.widget_attrs(fake_widget).get(DEFAULT_MAX_CHOICES_ATTR), str(MAX_CHOICES)
        )

    def test_get_prep_value_uses_codec_delimiter(self):
        ff = SelectMultipleFormField()
        with patch("select_multiple_field.codecs._DELIMITER", ";"):
            self.assertEqual(ff.get_prep_value(["a", "b"]), "a;b")
