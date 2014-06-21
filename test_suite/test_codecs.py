# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import SimpleTestCase

from select_multiple_field.codecs import (
    decode_csv_to_list, encode_list_to_csv)


class CodecTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = (
            ('a', 'Alpha'),
            ('b', 'Bravo'),
            ('c', 'Charlie'),
        )
        self.test_list = ['a', 'b', 'c']
        self.test_encoded = 'a,b,c'
        self.wild_delimiter = 'シ'
        self.test_encoded_alt = 'aシbシc'

    def test_decoder(self):
        decoded = decode_csv_to_list(self.test_encoded)
        self.assertEqual(decoded, self.test_list)
        decoded = decode_csv_to_list(self.test_encoded[0:1])
        self.assertEqual(decoded, self.test_list[0:1])

    def test_decoder_on_empty_string(self):
        decoded = decode_csv_to_list('')
        self.assertEqual(decoded, [])

    def test_decoder_on_single_encoded_character(self):
        single_encoded = self.choices[1][0]
        decoded = decode_csv_to_list(single_encoded)
        self.assertEqual(decoded, [single_encoded])

    def test_decoder_deduplicates(self):
        decoded = decode_csv_to_list(self.test_encoded + ',b,c,c')
        self.assertEqual(decoded, self.test_list)

    def test_decoder_delimiter(self):
        with self.settings(SELECTMULTIPLEFIELD_DELIMITER=self.wild_delimiter):
            decoded = decode_csv_to_list(self.test_encoded_alt)
            self.assertEqual(decoded, self.test_list)

    def test_encoder(self):
        encoded = encode_list_to_csv(self.test_list)
        self.assertEqual(encoded, self.test_encoded)
        encoded = encode_list_to_csv(self.test_list[0:1])
        self.assertEqual(encoded, self.test_encoded[0:1])

    def test_encoder_on_empty_list(self):
        encoded = encode_list_to_csv([])
        self.assertEqual(encoded, '')

    def test_encoder_deduplicates(self):
        encoded = encode_list_to_csv(self.test_list * 3)
        self.assertEqual(encoded, self.test_encoded)

    def test_encoder_delimiter(self):
        with self.settings(SELECTMULTIPLEFIELD_DELIMITER=self.wild_delimiter):
            encoded = encode_list_to_csv(self.test_list)
            self.assertEqual(encoded, self.test_encoded_alt)
