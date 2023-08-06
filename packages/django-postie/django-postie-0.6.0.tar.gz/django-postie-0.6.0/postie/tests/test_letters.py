from smtplib import SMTPException
from unittest import mock

from django import test
from django.core import mail
from django.test import override_settings
from django_dynamic_fixture import G

from ..models import Letter as LetterModel, Log
from ..entities import Letter
from ..const import LETTER_STATUSES


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
)
class ValidMailLetterTestCase(test.TestCase):
    model = LetterModel

    def test_send_email_logs_none(self):
        letter = G(
            self.model,
            subject='Text',
            plain='Text',
            recipients='user@gmail.com'
        )
        Letter(letter).send()

        self.assertEqual(Log.objects.count(), 0)

    def test_send_email_letter_status_sent(self):
        letter = G(
            self.model,
            subject='Text',
            plain='Text',
            recipients='user@gmail.com'
        )
        Letter(letter).send()
        letter.refresh_from_db()
        self.assertEqual(letter.status, LETTER_STATUSES.sent)

    def test_send_email_one_receiver_recipients(self):
        letter = G(
            self.model,
            subject='Text',
            plain='<b>Text</b>',
            recipients='user@gmail.com'
        )
        Letter(letter).send()

        self.assertEqual(mail.outbox[0].to[0], 'user@gmail.com')

    def test_send_email_many_receivers_recipients(self):
        letter = G(
            self.model,
            subject='Text',
            plain='<b>Text</b>',
            recipients='user@gmail.com,admin@gmail.com'
        )
        Letter(letter).send()

        self.assertListEqual(
            mail.outbox[0].to, ['user@gmail.com', 'admin@gmail.com']
        )


class FailMailLetterTestCase(test.TestCase):
    model = LetterModel

    def setUp(self):
        self.patcher = mock.patch('django.core.mail.EmailMultiAlternatives.send')
        self.addCleanup(self.patcher.stop)

        self.mock = self.patcher.start()
        self.mock.side_effect = SMTPException('Send message failed!')

    def test_send_email_letter_status_fail(self):
        letter = G(
            self.model,
            subject='Text',
            plain='<b>Text</b>',
            recipients='user@gmail.com'
        )
        Letter(letter).send()
        letter.refresh_from_db()
        self.assertEqual(letter.status, LETTER_STATUSES.failed)

    def test_send_email_log_created(self):
        letter = G(
            self.model,
            subject='Text',
            plain='<b>Text</b>',
            recipients='user@gmail.com'
        )
        Letter(letter).send()

        self.assertEqual(Log.objects.count(), 1)

