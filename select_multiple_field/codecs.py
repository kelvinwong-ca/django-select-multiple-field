# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


DEFAULT_DELIMITER = ','


def decode_csv_to_list(encoded):
    """
    Decodes a delimiter separated string to a Python list
    """
    delimiter = getattr(
        settings, 'SELECTMULTIPLEFIELD_DELIMITER', DEFAULT_DELIMITER)
    return sorted(encoded.split(delimiter))


def encode_list_to_csv(decoded):
    """
    Encodes a Python list to a delimiter separated string

    Note: This sorts the list lexicographically
    """
    delimiter = getattr(
        settings, 'SELECTMULTIPLEFIELD_DELIMITER', DEFAULT_DELIMITER)
    decoded.sort()
    return delimiter.join(decoded)