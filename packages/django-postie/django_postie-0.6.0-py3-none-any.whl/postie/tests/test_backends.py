from unittest.mock import patch

from django import test
from django.core import mail

from django_dynamic_fixture import G

from ..backends import CeleryEmailBackend, EmailBackend
from ..models import Letter as LetterModel
from ..entities import Letter

__all__ = (
    'TestSendMailUseCase',
)


class TestSendMailUseCase(test.TestCase):
    def test_instant_send(self):
        letter = G(LetterModel)
        entity = Letter(letter)

        with self.settings(POSTIE_INSTANT_SEND=True):
            EmailBackend().send(entity)
            self.assertEqual(len(mail.outbox), 1)

    @test.override_settings(POSTIE_INSTANT_SEND=False)
    def test_celery_send(self):
        letter = G(LetterModel)
        entity = Letter(letter)

        with patch('postie.tasks.send_letter.delay'):
            CeleryEmailBackend().send(entity)
            self.assertEqual(len(mail.outbox), 0)
