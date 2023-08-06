from pathlib import Path

from django import test
from django.core import mail

from ..tasks import send_letter
from ..models import Letter, Attachment
from ..const import LETTER_STATUSES

__all__ = (
    'LetterSendTestCase'
)


class LetterSendTestCase(test.TestCase):
    def test_wrong_letter_raised_error(self):
        with self.assertRaises(ValueError):
            send_letter(2)

    def test_lettter_without_files_send(self):
        letter = Letter.objects.create(
            email_from='cyberbudy@gmail.com',
            subject='Subject',
            html='<b>Mail body</b>',
            plain='Mail body',
            recipients='cyberbudy@gmail.com'
        )

        send_letter(letter.id)
        letter.refresh_from_db()
        self.assertEqual(letter.status, LETTER_STATUSES.sent)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, letter.subject)

    def test_lettter_with_files_send(self):
        letter = Letter.objects.create(
            email_from='cyberbudy@gmail.com',
            subject='Subject',
            html='<b>Mail body</b>',
            plain='Mail body',
            recipients='cyberbudy@gmail.com'
        )
        Attachment(
            letter=letter,
            attachment=open(Path(__file__).parent / 'file_fixture.json')
        )

        send_letter(letter.id)
        letter.refresh_from_db()

        self.assertEqual(letter.status, LETTER_STATUSES.sent)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, letter.subject)
