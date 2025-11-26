from unittest.mock import patch

from django.test import SimpleTestCase

from select_multiple_field.codecs import decode_csv_to_list, encode_list_to_csv


class CodecTestCase(SimpleTestCase):

    def setUp(self):
        self.choices = (
            ("a", "Alpha"),
            ("b", "Bravo"),
            ("c", "Charlie"),
        )
        self.test_list = ["a", "b", "c"]
        self.test_encoded = "a,b,c"
        self.wild_delimiter = "シ"
        self.test_encoded_alt = "aシbシc"

    def test_decoder_basic(self):
        decoded = decode_csv_to_list(self.test_encoded)
        self.assertEqual(decoded, self.test_list)
        decoded = decode_csv_to_list(self.test_encoded[0:1])
        self.assertEqual(decoded, self.test_list[0:1])

    def test_decoder_on_empty_string(self):
        decoded = decode_csv_to_list("")
        self.assertEqual(decoded, [])

    def test_decoder_on_single_encoded_character(self):
        single_encoded = self.choices[1][0]
        decoded = decode_csv_to_list(single_encoded)
        self.assertEqual(decoded, [single_encoded])

    def test_decoder_preserves_duplicates(self):
        """Decoder should preserve duplicate values, not deduplicate."""
        decoded = decode_csv_to_list("a,b,a,c,b")
        self.assertEqual(decoded, ["a", "b", "a", "c", "b"])

    def test_decoder_delimiter(self):
        with patch("select_multiple_field.codecs._DELIMITER", self.wild_delimiter):
            decoded = decode_csv_to_list(self.test_encoded_alt)
            self.assertEqual(decoded, self.test_list)

    def test_decoder_preserves_order(self):
        """Decoder should preserve original order, not sort alphabetically."""
        decoded = decode_csv_to_list("z,a,m")
        self.assertEqual(decoded, ["z", "a", "m"])

    def test_encoder_basic(self):
        encoded = encode_list_to_csv(self.test_list)
        self.assertEqual(encoded, self.test_encoded)
        encoded = encode_list_to_csv(self.test_list[0:1])
        self.assertEqual(encoded, self.test_encoded[0:1])

    def test_encoder_on_empty_list(self):
        encoded = encode_list_to_csv([])
        self.assertEqual(encoded, "")

    def test_encoder_preserves_duplicates(self):
        """Encoder should preserve duplicate values, not deduplicate."""
        encoded = encode_list_to_csv(["a", "b", "a", "c", "b"])
        self.assertEqual(encoded, "a,b,a,c,b")

    def test_encoder_delimiter(self):
        with patch("select_multiple_field.codecs._DELIMITER", self.wild_delimiter):
            encoded = encode_list_to_csv(self.test_list)
            self.assertEqual(encoded, self.test_encoded_alt)

    def test_encoder_preserves_order(self):
        """Encoder should preserve original list order, not sort alphabetically."""
        encoded = encode_list_to_csv(["z", "a", "m"])
        self.assertEqual(encoded, "z,a,m")

    def test_roundtrip_preserves_order_and_duplicates(self):
        """Round-trip encode/decode should preserve order and duplicates."""
        original = ["z", "a", "m", "a", "z"]
        encoded = encode_list_to_csv(original)
        decoded = decode_csv_to_list(encoded)
        self.assertEqual(decoded, original)
