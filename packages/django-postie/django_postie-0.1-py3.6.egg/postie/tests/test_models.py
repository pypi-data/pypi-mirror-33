from django import test

from django_dynamic_fixture import G

from ..const import LETTER_STATUSES
from ..models import Letter

__all__ = (
    'LetterTestCase',
)


class LetterTestCase(test.TestCase):
    def test_sent_query_method(self):
        G(Letter, status=LETTER_STATUSES.draft, n=5)
        G(Letter, status=LETTER_STATUSES.sent, n=5)
        G(Letter, status=LETTER_STATUSES.failed, n=5)

        self.assertEqual(Letter.objects.sent().count(), 5)

    def test_not_sent_query_method(self):
        G(Letter, status=LETTER_STATUSES.draft, n=5)
        G(Letter, status=LETTER_STATUSES.sent, n=5)
        G(Letter, status=LETTER_STATUSES.failed, n=5)

        self.assertEqual(Letter.objects.sent().count(), 5)
