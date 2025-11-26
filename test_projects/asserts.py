import sys

import django


def safe_assert_redirects(test_case, response, expected_url):
    """
    Workaround for Python 3.14 + Django 4.2 assertRedirects incompatibility.
    """
    if sys.version_info >= (3, 14) and django.VERSION[:2] == (4, 2):
        test_case.assertEqual(response.status_code, 302)
        test_case.assertEqual(response.url, expected_url)
    else:
        test_case.assertRedirects(response, expected_url)
