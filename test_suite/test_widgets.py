# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.test import SimpleTestCase
from django.utils.datastructures import MergeDict, MultiValueDict

from select_multiple_field.widgets import (
    HTML_ATTR_CLASS, SelectMultipleField)


class SelectMultipleFieldTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = (
            ('a', 'Alpha'),
            ('b', 'Bravo'),
            ('c', 'Charlie'),
        )

    def test_instantiation(self):
        w = SelectMultipleField()
        self.assertIsInstance(w, widgets.SelectMultiple)

    def test_has_select_multiple_class(self):
        """Rendered widget has a useful HTML class attribute"""
        w = SelectMultipleField()
        tag = w.render('test', self.choices[1][0], choices=self.choices)
        self.assertEqual(tag.count(HTML_ATTR_CLASS), 1)

    def test_html_attr_class_settable(self):
        """Rendered widget can override HTML class attribute"""
        CUSTOM_HTML_CLASS = 'myowncss'
        attrs = {'class': CUSTOM_HTML_CLASS}
        w = SelectMultipleField()
        tag = w.render('test', self.choices[1][0], attrs, self.choices)
        self.assertEqual(tag.count(CUSTOM_HTML_CLASS), 1)
        self.assertEqual(tag.count(HTML_ATTR_CLASS), 0)

    def test_value_from_datadict(self):
        """Widget generates expected Python list-like object or None"""
        #
        # I know that this tests Django code. Humor me pls.
        #
        w = SelectMultipleField()
        name = 'test'
        data = {
            name: [self.choices[0][0], self.choices[2][0]]
        }
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
        #
        # MergeDict are generated from QueryDict which are subclasses of
        # MultiValueDict
        #
        data_obj = MergeDict(MultiValueDict(data))
        obj = w.value_from_datadict(data_obj, None, name)
        self.assertIsInstance(obj, list)
        self.assertIn(self.choices[0][0], obj)
        self.assertNotIn(self.choices[1][0], obj)
        self.assertIn(self.choices[2][0], obj)
