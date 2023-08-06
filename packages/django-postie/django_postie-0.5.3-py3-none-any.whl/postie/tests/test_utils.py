from django.test import TestCase
from django.conf import settings
from django.core.cache import cache

from ..utils import get_domain, get_protocol, default_language


__all__ = (
    'UtilsTestCase',
)

class UtilsTestCase(TestCase):
    def test_get_domain(self):
        site_name = get_domain()
        self.assertEqual(site_name, 'example.com')

    def test_get_protocol(self):
        self.assertEqual(get_protocol(), 'http')

        with self.settings(USE_HTTPS=True):
            self.assertEqual(get_protocol(), 'https')

    def test_default_language(self):
        # No parler settings
        with self.settings(PARLER_LANGUAGES={}):
            self.assertEqual(default_language(), settings.LANGUAGE_CODE)

        # With parler settings
        with self.settings(PARLER_LANGUAGES={'default': {'fallback': 'ru',}}):
            self.assertEqual(default_language(), 'ru')
