from django.conf import settings

from . import DEFAULT_DELIMITER

delimiter = getattr(settings, "SELECTMULTIPLEFIELD_DELIMITER", DEFAULT_DELIMITER)
if len(delimiter) != 1:
    raise ValueError("SELECTMULTIPLEFIELD_DELIMITER must be exactly one character")
_DELIMITER = delimiter


def decode_csv_to_list(encoded):
    """
    Decodes a delimiter separated string to a Python list.

    Preserves order and duplicates (no sorting, no deduplication).
    """
    if encoded == "":
        return []

    return encoded.split(_DELIMITER)


def encode_list_to_csv(decoded):
    """
    Encodes a Python list to a delimiter separated string.

    Preserves order and duplicates (no sorting, no deduplication).
    """
    return _DELIMITER.join(decoded)
