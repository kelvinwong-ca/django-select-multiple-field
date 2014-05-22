#-*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import SimpleTestCase
from django.utils.six.moves import xrange

from select_multiple_field.codecs import (
    DEFAULT_DELIMITER, decode_csv_to_list, encode_list_to_csv)


class CodecTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = (
            ('a', 'Alpha'),
            ('b', 'Bravo'),
            ('c', 'Charlie'),
        )
        self.test_list = ['a', 'b', 'c']
        self.test_encoded = 'a,b,c'

    def test_decoder(self):
        decoded = decode_csv_to_list(self.test_encoded)
        self.assertEqual(decoded, self.test_list)


# class StarToolsTestCase(SimpleTestCase):
# 
#     def setUp(self):
#         self.star_set = {
#             'star': 's',
#             'unlit': 'u',
#             'noanswer': 'n'
#         }
# 
#     def test_render_stars(self):
#         max_test_stars = 50
#         for max_stars in xrange(1, max_test_stars + 1):
#             for num in xrange(max_stars + 1):
#                 stars = render_stars(num, max_stars, self.star_set)
#                 self.assertEqual(len(stars), max_stars)
#                 self.assertEqual(stars.count(self.star_set['star']), num)
#                 self.assertEqual(
#                     stars.count(self.star_set['unlit']), max_stars - num)
# 
#     def test_render_stars_none(self):
#         """
#         By design items with no answer are stored as NULL which are converted
#         to None by the ORM. They are rendered as a ban icon which looks
#         similar enough to the empty set.
#         """
#         stars = render_stars(None, 5, self.star_set)
#         self.assertEqual(len(stars), 1)
#         self.assertEqual(stars.count(self.star_set['noanswer']), 1)
# 
#     def test_render_stars_blank(self):
#         """
#         If your database is storing numbers as strings you might need this.
#         Empty strings holding non answered items are rendered as a ban symbol.
#         """
#         stars = render_stars('', 5, self.star_set)
#         self.assertEqual(len(stars), 1)
#         self.assertEqual(stars.count(self.star_set['noanswer']), 1)
# 
#     def test_num_greater_than_max_error(self):
#         """
#         When the number of stars scored exceeds the maximum stars displayed,
#         just display the maximum stars allowed
#         """
#         num = 4
#         max_stars = 3
#         self.assertTrue(num > max_stars)
#         stars = render_stars(4, 3, self.star_set)
#         self.assertEqual(len(stars), max_stars)
#         self.assertEqual(stars.count(self.star_set['star']), max_stars)
#         self.assertEqual(stars.count(self.star_set['unlit']), 0)
# 
#     def test_render_string_numbers(self):
#         """
#         String representations of integers are rendered in the usual manner
#         """
#         max_test_stars = 50
#         for max_stars in xrange(1, max_test_stars + 1):
#             for num in xrange(max_stars + 1):
#                 num = str(num)
#                 max_stars = str(max_stars)
#                 stars = render_stars(num, max_stars, self.star_set)
#                 self.assertEqual(len(stars), int(max_stars))
#                 self.assertEqual(stars.count(self.star_set['star']), int(num))
#                 self.assertEqual(
#                     stars.count(self.star_set['unlit']),
#                     int(max_stars) - int(num))
