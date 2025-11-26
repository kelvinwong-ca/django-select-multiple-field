from django.forms import widgets
from django.forms.renderers import get_default_renderer
from django.test import SimpleTestCase
from django.utils.datastructures import MultiValueDict

from select_multiple_field.widgets import HTML_ATTR_CLASS, SelectMultipleWidget


class SelectMultipleWidgetTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = (
            ("a", "Alpha"),
            ("b", "Bravo"),
            ("c", "Charlie"),
        )

    def test_instantiation(self):
        w = SelectMultipleWidget()
        self.assertIsInstance(w, widgets.SelectMultiple)

    def test_has_select_multiple_class(self):
        """Rendered widget has a useful HTML class attribute"""
        w = SelectMultipleWidget()
        tag = w.render("test", self.choices[1][0], choices=self.choices)
        self.assertEqual(tag.count(HTML_ATTR_CLASS), 1)

    def test_html_attr_class_settable(self):
        """Rendered widget can override HTML class attribute"""
        CUSTOM_HTML_CLASS = "myowncss"
        attrs = {"class": CUSTOM_HTML_CLASS}
        w = SelectMultipleWidget()
        tag = w.render("test", self.choices[1][0], attrs, self.choices)
        self.assertEqual(tag.count(CUSTOM_HTML_CLASS), 1)
        self.assertEqual(tag.count(HTML_ATTR_CLASS), 0)

    def test_render_does_not_mutate_choices(self):
        """render() with choices must not permanently change self.choices"""
        w = SelectMultipleWidget()
        original = self.choices
        tag = w.render("test", "a", choices=original)
        self.assertEqual(w.choices, [])
        # self.choices was never set, should still be []

    def test_render_with_choices_restores_original(self):
        """render() with choices restores original self.choices"""
        w = SelectMultipleWidget(choices=self.choices)
        other_choices = (("x", "Xray"), ("y", "Yankee"))
        tag = w.render("test", "a", choices=other_choices)
        self.assertEqual(list(w.choices), list(self.choices))

    def test_multiple_renders_different_choices(self):
        """Multiple render() calls with different choices don't bleed"""
        w = SelectMultipleWidget(choices=self.choices)
        choices_a = (("x", "Xray"), ("y", "Yankee"))
        choices_b = (("1", "One"), ("2", "Two"))
        tag_a = w.render("test", "x", choices=choices_a)
        tag_b = w.render("test", "1", choices=choices_b)
        self.assertIn("Xray", tag_a)
        self.assertNotIn("One", tag_a)
        self.assertIn("One", tag_b)
        self.assertNotIn("Xray", tag_b)
        self.assertEqual(list(w.choices), list(self.choices))

    def test_render_without_choices_arg(self):
        """render() without choices uses self.choices"""
        w = SelectMultipleWidget(choices=self.choices)
        tag = w.render("test", "a")
        self.assertIn("Alpha", tag)
        self.assertIn("Bravo", tag)
        self.assertIn("Charlie", tag)

    def test_render_with_none_value(self):
        """render() with value=None converts to empty list (no crash)"""
        w = SelectMultipleWidget(choices=self.choices)
        tag = w.render("test", None)
        self.assertIn("Alpha", tag)

    def test_render_with_explicit_renderer(self):
        """render() accepts an explicit renderer parameter"""
        w = SelectMultipleWidget(choices=self.choices)
        renderer = get_default_renderer()
        tag = w.render("test", "a", renderer=renderer)
        self.assertIn("Alpha", tag)
        self.assertIn("select-multiple-field", tag)

    def test_value_from_datadict(self):
        """Widget generates expected Python list-like object or None"""
        #
        # I know that this tests Django code. Humor me pls.
        #
        w = SelectMultipleWidget()
        name = "test"
        data = {name: [self.choices[0][0], self.choices[2][0]]}
        #
        # dict miss returns None
        #
        obj = w.value_from_datadict({}, None, name)
        self.assertIs(obj, None)
        #
        # Plain dict returns obj in value, usually a list
        #
        obj = w.value_from_datadict(data, None, name)
        self.assertIsInstance(obj, list)
        self.assertIn(self.choices[0][0], obj)
        self.assertNotIn(self.choices[1][0], obj)
        self.assertIn(self.choices[2][0], obj)
        #
        # MultiValueDict are generated from WSGIRequest
        #
        data_obj = MultiValueDict(data)
        obj = w.value_from_datadict(data_obj, None, name)
        self.assertIsInstance(obj, list)
        self.assertIn(self.choices[0][0], obj)
        self.assertNotIn(self.choices[1][0], obj)
        self.assertIn(self.choices[2][0], obj)
