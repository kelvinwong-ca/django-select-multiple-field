import collections
import string
import warnings
from unittest import skipIf
from unittest.mock import patch

import django
from django.core import validators
from django.core.exceptions import ValidationError
from django.db.models.fields import BLANK_CHOICE_DASH, CharField, Field
from django.test import SimpleTestCase

from select_multiple_field.codecs import encode_list_to_csv
from select_multiple_field.forms import SelectMultipleFormField
from select_multiple_field.models import SelectMultipleField
from select_multiple_field.validators import (
    MaxLengthValidator as CustomMaxLengthValidator,
)


class FakeCallableDefault:
    pass


class SelectMultipleFieldTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = tuple([(c, c) for c in string.ascii_letters])
        self.choices_list = [c[0] for c in self.choices[0 : len(self.choices)]]
        self.choices_str = "a,b"
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
            (self.optgroup_choices, self.optgroup_choices_list),
        ]

    def test_instantiation(self):
        item = SelectMultipleField()
        self.assertIsInstance(item, Field)

    def test_instantiation_max_choices(self):
        for max_choices in range(1, 25):
            item = SelectMultipleField(max_choices=max_choices)
            self.assertEqual(item.max_choices, max_choices)

    def test_instantiation_include_blank(self):
        """Keep for migration compatibility"""
        item = SelectMultipleField(include_blank=False)
        self.assertFalse(item.include_blank)
        item = SelectMultipleField(include_blank=True)
        self.assertTrue(item.include_blank)

    def test_instantiation_max_choices_none_explicit(self):
        """Explicit max_choices=None should not add MaxChoicesValidator"""
        item = SelectMultipleField(max_choices=None)
        self.assertIsNone(item.max_choices)
        # Should not have MaxChoicesValidator
        validator_types = [type(v).__name__ for v in item.validators]
        self.assertNotIn("MaxChoicesValidator", validator_types)

    def test_instantiation_include_blank_kwargs_override(self):
        """
        When include_blank is set on field, kwargs should be ignored in get_choices

        Keep for migration compatibility
        """
        item = SelectMultipleField(choices=self.choices, include_blank=True)
        self.assertTrue(item.include_blank)
        self.assertTrue(item._include_blank_set)
        # kwargs include_blank should be ignored
        choices = item.get_choices(include_blank=False)
        self.assertIn(BLANK_CHOICE_DASH[0], choices)

        # When not set on field, kwargs should be respected
        item2 = SelectMultipleField(choices=self.choices)
        choices2 = item2.get_choices(include_blank=True)
        self.assertIn(BLANK_CHOICE_DASH[0], choices2)

    def test_instantiation_include_blank_false_explicit(self):
        """
        Explicit include_blank=False should be serialized in deconstruct

        Keep for migration compatibility
        """
        item = SelectMultipleField(include_blank=False)
        self.assertFalse(item.include_blank)
        self.assertTrue(item._include_blank_set)

    def test_instantiation_combined_params(self):
        """
        Combined max_choices and include_blank

        Keep for migration compatibility
        """
        item = SelectMultipleField(max_choices=3, include_blank=True)
        self.assertEqual(item.max_choices, 3)
        self.assertTrue(item.include_blank)
        self.assertTrue(item._include_blank_set)
        validator_types = [type(v).__name__ for v in item.validators]
        self.assertIn("MaxChoicesValidator", validator_types)

    def test_instantiation_kwargs_not_mutated(self):
        """Original kwargs dict should not be mutated (BUGS.md #16)"""
        kwargs = {"max_choices": 2, "include_blank": True, "max_length": 10}
        original = kwargs.copy()
        SelectMultipleField(**kwargs)
        self.assertEqual(kwargs, original)

    def test_instantiation_auto_max_length(self):
        """max_length auto-calculated when not provided but choices + max_choices are"""
        choices = [("a", "a"), ("bb", "bb"), ("ccc", "ccc")]
        item = SelectMultipleField(choices=choices, max_choices=2)
        # longest 2 choices joined by comma: "ccc,bb" = 6 chars
        self.assertEqual(item.max_length, 6)

    def test_instantiation_auto_max_length_max_choices_gt_choices(self):
        """max_length uses all choices when max_choices > available choices"""
        choices = [("a", "a"), ("bb", "bb")]
        item = SelectMultipleField(choices=choices, max_choices=10)
        # all choices joined: "bb,a" = 4 chars
        self.assertEqual(item.max_length, 4)

    def test_instantiation_auto_max_length_no_auto_without_choices(self):
        """No auto-calculation when choices not provided"""
        item = SelectMultipleField(max_choices=2, max_length=10)
        self.assertEqual(item.max_length, 10)

    def test_instantiation_auto_max_length_no_auto_without_max_choices(self):
        """No auto-calculation when max_choices not provided"""
        choices = [("a", "a"), ("bb", "bb")]
        item = SelectMultipleField(choices=choices, max_length=10)
        self.assertEqual(item.max_length, 10)

    def test_instantiation_auto_max_length_warning(self):
        """Warning issued when explicit max_length < calculated maximum"""
        choices = [("a", "a"), ("bb", "bb"), ("ccc", "ccc")]
        with self.assertWarns(RuntimeWarning) as cm:
            SelectMultipleField(choices=choices, max_choices=2, max_length=3)
        self.assertIn("too small", str(cm.warning))

    def test_instantiation_auto_max_length_no_warning(self):
        """No warning when explicit max_length >= calculated maximum"""
        choices = [("a", "a"), ("bb", "bb"), ("ccc", "ccc")]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            SelectMultipleField(choices=choices, max_choices=2, max_length=6)
            self.assertEqual(len(w), 0)

    def test_calculate_max_encoded_length_optgroups(self):
        """_calculate_max_encoded_length works with optgroup choices"""
        optgroups = [
            ("group1", [("aa", "aa"), ("b", "b")]),
            ("group2", [("c", "c")]),
        ]
        item = SelectMultipleField(choices=optgroups, max_choices=2)
        # longest 2 keys: "aa" + "," + "c" = 5, but
        # get_choices_keys() flattens to ['aa', 'b', 'c'], so
        # longest 2 joined: "aa,c" = 4 chars
        self.assertEqual(item.max_length, 4)

    def test_instantiation_max_choices_validation(self):
        """max_choices should be positive integer"""
        with self.assertRaises((ValueError, TypeError)):
            SelectMultipleField(max_choices=0)
        with self.assertRaises((ValueError, TypeError)):
            SelectMultipleField(max_choices=-1)
        with self.assertRaises((ValueError, TypeError)):
            SelectMultipleField(max_choices="invalid")

    def test_instantiation_include_blank_validation(self):
        """
        include_blank should be boolean

        Keep for migration compatibility
        """
        with self.assertRaises((ValueError, TypeError)):
            SelectMultipleField(include_blank="invalid")
        with self.assertRaises((ValueError, TypeError)):
            SelectMultipleField(include_blank=1)

    def test_validator_replaces_maxlengthvalidator(self):
        """CharField's built-in MaxLengthValidator removed"""
        item = SelectMultipleField(max_length=100)
        django_maxlength = [
            v
            for v in item.validators
            if type(v).__name__ == "MaxLengthValidator"
            and type(v).__module__ == "django.core.validators"
        ]
        custom_maxlength = [
            v for v in item.validators if isinstance(v, CustomMaxLengthValidator)
        ]
        self.assertEqual(
            len(django_maxlength), 0, "Django's MaxLengthValidator should be removed"
        )
        self.assertEqual(
            len(custom_maxlength), 1, "Custom MaxLengthValidator should be present"
        )

    def test_deconstruct_max_choices(self):
        """deconstruct() should include max_choices when set"""
        item = SelectMultipleField(max_choices=5)
        name, path, args, kwargs = item.deconstruct()
        self.assertEqual(kwargs.get("max_choices"), 5)

    def test_deconstruct_max_choices_none(self):
        """deconstruct() should not include max_choices when None"""
        item = SelectMultipleField(max_choices=None)
        name, path, args, kwargs = item.deconstruct()
        self.assertNotIn("max_choices", kwargs)

    def test_deconstruct_include_blank_true(self):
        """
        deconstruct() should include include_blank when True and explicitly set

        Keep for migration compatibility
        """
        item = SelectMultipleField(include_blank=True)
        name, path, args, kwargs = item.deconstruct()
        self.assertTrue(kwargs.get("include_blank"))

    def test_deconstruct_include_blank_false(self):
        """
        deconstruct() should include include_blank when False and explicitly set

        Keep for migration compatibility
        """
        item = SelectMultipleField(include_blank=False)
        name, path, args, kwargs = item.deconstruct()
        self.assertFalse(kwargs.get("include_blank"))

    def test_deconstruct_include_blank_not_set(self):
        """
        deconstruct() should not include include_blank when not explicitly set

        Keep for migration compatibility
        """
        item = SelectMultipleField()
        name, path, args, kwargs = item.deconstruct()
        self.assertNotIn("include_blank", kwargs)

    def test_instantiation_null_no_deprecation_warning(self):
        """null=True is now supported without deprecation warning"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            item = SelectMultipleField(null=True)
            self.assertEqual(len(w), 0)
            self.assertTrue(item.null)

    def test_get_internal_type(self):
        item = SelectMultipleField()
        charfield = CharField()
        self.assertEqual(item.get_internal_type(), charfield.get_internal_type())

    def test_get_prep_value_none(self):
        """None stored as NULL in db when null=True, else empty string"""
        item = SelectMultipleField()
        self.assertEqual(item.get_prep_value(None), "")
        item_null = SelectMultipleField(null=True)
        self.assertIsNone(item_null.get_prep_value(None))

    def test_get_prep_value_empty_list(self):
        """No choice stored as empty string"""
        item = SelectMultipleField()
        self.assertIsInstance(item.get_prep_value([]), str)
        self.assertEqual(item.get_prep_value([]), "")

    def test_get_prep_value_empty_list_null(self):
        """No choice stored as NULL when null=True"""
        item = SelectMultipleField(null=True)
        self.assertIsNone(item.get_prep_value([]))

    def test_get_prep_value_list(self):
        item = SelectMultipleField()
        self.assertIsInstance(item.get_prep_value(self.choices_list), str)

    def test_from_db_value_none(self):
        """A None value from the db is interpreted as no choice (empty list)"""
        item = SelectMultipleField()
        self.assertIsInstance(item.from_db_value(None, None, None, None), list)
        self.assertEqual(item.from_db_value(None, None, None, None), [])

    def test_from_db_value_empty_string(self):
        """An empty string value from the db is interpreted as no choice (empty list)"""
        item = SelectMultipleField()
        self.assertIsInstance(item.from_db_value("", None, None, None), list)
        self.assertEqual(item.from_db_value("", None, None, None), [])

    def test_from_db_value_list(self):
        """Simple string from db is decoded to list. See codecs for more tests."""
        item = SelectMultipleField()
        self.assertIsInstance(
            item.from_db_value("A,B", None, None, None),
            list,
        )
        self.assertEqual(
            item.from_db_value("A,B", None, None, None),
            ["A", "B"],
        )

    def test_value_to_string(self):
        """value_to_string defers to value_from_object"""
        item = SelectMultipleField()
        self.assertTrue(hasattr(item, "value_to_string"))
        self.assertTrue(hasattr(item, "value_from_object"))

    def test_has_choices(self):
        """has_choices checks for choices/_choices"""
        no_choices = SelectMultipleField()
        self.assertFalse(no_choices.has_choices())

        with_choices = SelectMultipleField(choices=[("a", "A")])
        self.assertTrue(with_choices.has_choices())

    def test_validate_null_no_blank(self):
        """null=False, blank=True, value=None -> null error (not blank)"""
        item = SelectMultipleField()
        item.editable = True
        item.null = False
        item.blank = True
        with self.assertRaises(ValidationError) as cm:
            item.validate(None, "instance")
        self.assertEqual(
            cm.exception.messages[0],
            SelectMultipleField.default_error_messages["null"],
        )

    def test_to_python_none(self):
        item = SelectMultipleField()
        self.assertIsInstance(item.to_python(None), list)

    def test_to_python_empty_list(self):
        item = SelectMultipleField()
        self.assertIsInstance(item.to_python([]), list)
        self.assertEqual(item.to_python([]), [])

    def test_to_python_list(self):
        for choices, choices_list in self.test_choices:
            item = SelectMultipleField(choices=choices)
            self.assertTrue(item.choices)
            self.assertIsInstance(item.to_python(choices_list), list)
            self.assertEqual(item.to_python(choices_list), choices_list)

    def test_to_python_list_w_invalid_value(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertTrue(item.choices)
        invalid_list = ["InvalidChoice"]
        with self.assertRaises(ValidationError) as cm:
            item.to_python(invalid_list)

        self.assertEqual(
            cm.exception.messages[0],
            (
                SelectMultipleField.default_error_messages["invalid_choice"]
                % {"value": invalid_list}
            ),
        )

    def test_to_python_empty_string(self):
        item = SelectMultipleField()
        self.assertIsInstance(item.to_python(""), list)
        self.assertEqual(item.to_python(""), [])

    def test_to_python_single_string(self):
        item = SelectMultipleField()
        single = self.choices_list[3]
        self.assertIsInstance(item.to_python(single), list)
        self.assertEqual(item.to_python(single), [single])

    def test_to_python_string(self):
        item = SelectMultipleField()
        for i, v in enumerate(self.choices_list):
            subset = self.choices_list[0:i]
            encoded = encode_list_to_csv(subset)
            self.assertIsInstance(item.to_python(encoded), list)
            self.assertEqual(item.to_python(encoded), subset)

    def test_to_python_invalid_type(self):
        item = SelectMultipleField()
        invalid_type = True
        with self.assertRaises(ValidationError) as cm:
            item.to_python(invalid_type)

        self.assertEqual(
            cm.exception.messages[0],
            (
                SelectMultipleField.default_error_messages["invalid_type"]
                % {"value": type(invalid_type)}
            ),
        )

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

        Keep for migration compatibility
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
                subset = self.choices_list[0 : i + 1]
                self.assertIs(item.validate(subset, instance), None)

    def test_validate_not_editable(self):
        item = SelectMultipleField()
        item.editable = False
        value = "Any Value"
        instance = "Fake Unused Instance"
        self.assertIs(item.validate(value, instance), None)

    def test_validate_invalid_choice_iterable(self):
        iv = ["Invalid Choice"]
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate(iv, "Fake Unused Instance"))

        self.assertEqual(
            cm.exception.messages[0],
            (
                SelectMultipleField.default_error_messages["invalid_choice"]
                % {"value": iv}
            ),
        )

    def test_validate_invalid_choice_string(self):
        """
        Invalid string value is decoded to list before validation

        "a,b,InvalidChoice" is decoded to ["a", "b", "InvalidChoice"] before validation
        so ["InvalidChoice"] is in the error message
        """
        ivc = "InvalidChoice"
        iv = self.choices_str + f",{ivc}"  # a,b,InvalidChoice

        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate(iv, "Fake Unused Instance"))

        self.assertEqual(
            cm.exception.messages[0],
            (
                SelectMultipleField.default_error_messages["invalid_choice"]
                % {"value": [ivc]}
            ),
        )

    def test_validate_invalid_string(self):
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        value = "Invalid Choice"
        instance = "Fake Unused Instance"
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate(value, instance))

        # String value is decoded to list before validation, so error
        # message contains the decoded list form
        self.assertEqual(
            cm.exception.messages[0],
            (
                SelectMultipleField.default_error_messages["invalid_choice"]
                % {"value": [value]}
            ),
        )

    def test_validate_not_null(self):
        """
        None is converted to [] by to_python before validation,
        so validation checks for blank, not null
        """
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        item.null = False
        item.blank = False
        value = None
        instance = "Fake Unused Instance"
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate(value, instance))

        self.assertEqual(
            cm.exception.messages[0],
            SelectMultipleField.default_error_messages["blank"],
        )

    def test_validate_blank(self):
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        item.blank = True
        value = [""]
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
            SelectMultipleField.default_error_messages["blank"],
        )

    def test_validate_options_list(self):
        item = SelectMultipleField(choices=self.choices)
        value = self.choices_list
        self.assertIs(item.validate_options_list(value), None)

    def test_validate_options_list_raises_validationerror(self):
        item = SelectMultipleField(choices=self.choices)
        value = ["InvalidChoice"]
        with self.assertRaises(ValidationError) as cm:
            self.assertTrue(item.validate_options_list(value))

        self.assertEqual(
            cm.exception.messages[0],
            (
                SelectMultipleField.default_error_messages["invalid_choice"]
                % {"value": value}
            ),
        )

    def test_find_invalid_choices_all_valid(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertEqual(item._find_invalid_choices(self.choices_list), [])

    def test_find_invalid_choices_all_invalid(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertEqual(item._find_invalid_choices(["1", "2"]), ["1", "2"])

    def test_find_invalid_choices_mixed(self):
        item = SelectMultipleField(choices=self.choices)
        self.assertEqual(
            item._find_invalid_choices(["a", "notreal", "b", "bad"]),
            ["notreal", "bad"],
        )

    def test_find_invalid_choices_blank_skips_empty(self):
        item = SelectMultipleField(choices=self.choices, blank=True)
        self.assertEqual(item._find_invalid_choices(["a", "", "b"]), [])

    def test_custom_delimiter_get_prep_value(self):
        with patch("select_multiple_field.codecs._DELIMITER", ";"):
            item = SelectMultipleField()
            self.assertEqual(item.get_prep_value(["a", "b"]), "a;b")

    def test_custom_delimiter_from_db_value(self):
        with patch("select_multiple_field.codecs._DELIMITER", ";"):
            item = SelectMultipleField()
            self.assertEqual(item.from_db_value("a;b", None, None), ["a", "b"])

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

    def test_get_choices_keys_cache_returns_same_list(self):
        item = SelectMultipleField(choices=self.choices)
        first = item.get_choices_keys()
        second = item.get_choices_keys()
        self.assertIs(first, second, "cache should return same list object")

    def test_get_choices_keys_cache_per_instance(self):
        item_a = SelectMultipleField(choices=self.choices)
        item_b = SelectMultipleField(choices=self.choices)
        first = item_a.get_choices_keys()
        second = item_b.get_choices_keys()
        self.assertIsNot(first, second, "each instance has independent cache")
        self.assertEqual(first, second)

    def test_get_choices_keys_cache_used_by_validate(self):
        item = SelectMultipleField(choices=self.choices)
        item.editable = True
        instance = "Fake Unused Instance"
        first = item.get_choices_keys()
        item.validate(["a", "b"], instance)
        second = item.get_choices_keys()
        self.assertIs(first, second, "validate() should reuse cache")

    def test_get_choices_keys_cache_used_by_validate_option(self):
        item = SelectMultipleField(choices=self.choices)
        first = item.get_choices_keys()
        item.validate_option("a")
        second = item.get_choices_keys()
        self.assertIs(first, second, "validate_option() should reuse cache")

    @skipIf(django.VERSION < (5, 0), "Callable choices require Django 5.0+")
    def test_get_choices_keys_callable_invoked_once(self):
        calls = 0

        def dynamic_choices():
            nonlocal calls
            calls += 1
            return [("a", "A"), ("b", "B")]

        item = SelectMultipleField(choices=dynamic_choices)
        item.get_choices_keys()
        item.get_choices_keys()
        item.editable = True
        item.validate(["a"], "x")
        self.assertEqual(calls, 1, "callable should be invoked once due to caching")

    @skipIf(django.VERSION < (5, 0), "Callable choices require Django 5.0+")
    def test_callable_choices_validate_valid(self):
        item = SelectMultipleField(choices=lambda: [("a", "A"), ("b", "B")])
        item.editable = True
        item.validate(["a", "b"], None)

    @skipIf(django.VERSION < (5, 0), "Callable choices require Django 5.0+")
    def test_callable_choices_validate_invalid(self):
        item = SelectMultipleField(choices=lambda: [("a", "A"), ("b", "B")])
        item.editable = True
        with self.assertRaises(ValidationError):
            item.validate(["x"], None)

    @skipIf(django.VERSION < (5, 0), "Callable choices require Django 5.0+")
    def test_callable_choices_validate_option(self):
        item = SelectMultipleField(choices=lambda: [("a", "A"), ("b", "B")])
        self.assertTrue(item.validate_option("a"))
        self.assertFalse(item.validate_option("x"))

    @skipIf(django.VERSION < (5, 0), "Callable choices require Django 5.0+")
    def test_callable_choices_get_choices_keys(self):
        item = SelectMultipleField(choices=lambda: [("a", "A"), ("b", "B")])
        self.assertEqual(item.get_choices_keys(), ["a", "b"])

    def test_get_choices_keys_include_blank(self):
        """
        Keep for migration compatibility
        """
        item = SelectMultipleField(choices=self.choices)
        with_blank = item.get_choices_keys(include_blank=True)
        without_blank = item.get_choices_keys(include_blank=False)
        self.assertIn("", with_blank)
        self.assertNotIn("", without_blank)

    def test_get_choices_keys_kwargs_bypass_cache(self):
        item = SelectMultipleField(choices=self.choices)
        first = item.get_choices_keys()
        second = item.get_choices_keys(include_blank=True)
        third = item.get_choices_keys()
        self.assertIs(first, third, "no-kwargs calls share cache")
        self.assertIsNot(first, second, "kwargs call bypasses cache")

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
        self.assertTrue(item.blank)
        self.assertFalse(form.required)
        self.assertFalse(item.null)
        self.assertEqual(form.empty_value, [])
        self.assertIn(BLANK_CHOICE_DASH[0], form.choices)
