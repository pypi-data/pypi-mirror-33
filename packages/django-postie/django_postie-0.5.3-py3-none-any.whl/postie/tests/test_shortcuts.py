from pathlib import Path

from django import test
from django.core import mail

from django_dynamic_fixture import G

from ..shortcuts import send_mail
from ..models import Template

__all__ = (
    'SendMailTestCase'
)


class SendMailTestCase(test.TestCase):
    def setUp(self):
        self.new_events = (
            'event', '1'
        )

    def test_wrong_template_raised_error(self):
        with self.assertRaises(ValueError):
            send_mail(2, recipients=[], context={})

    def test_mail_without_files_send(self):
        with self.settings(POSTIE_TEMPLATE_CHOICES=self.new_events,
                POSTIE_INSTANT_SEND=True):

            template = G(
                Template,
                name='event',
                event='event',
                subject='Subject',
                html='<b>Mail body</b>',
                plain='Mail body',
            )
            template.subject = 'Subject'
            template.save()

            send_mail(
                event='event',
                from_email='cyberbudy@gmail.com',
                recipients=['cyberbudy@gmail.com'],
                context={}
            )

            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'Subject')

    def test_mail_with_files_send(self):
        with self.settings(POSTIE_TEMPLATE_CHOICES=self.new_events,
                POSTIE_INSTANT_SEND=True):
            template = G(
                Template,
                name='event',
                event='event',
                subject='Subject',
                html='<b>Mail body</b>',
                plain='Mail body',
            )
            template.subject = 'Subject'
            template.save()

            with open(Path(__file__).parent / 'file_fixture.json') as f:
                send_mail(
                    event='event',
                    from_email='cyberbudy@gmail.com',
                    recipients=['cyberbudy@gmail.com'],
                    context={},
                    attachments=[{
                        'file_fixtures': f
                    }]
                )

            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'Subject')

    def test_mail_with_unknown_language(self):
        with self.settings(POSTIE_TEMPLATE_CHOICES=self.new_events,
                POSTIE_INSTANT_SEND=True):
            template = G(
                Template,
                name='event',
                event='event',
                subject='Subject',
                html='<b>Mail body</b>',
                plain='Mail body',
            )
            template.subject = 'Subject'
            template.save()

            with self.assertRaises(ValueError):
                send_mail(
                    event='event',
                    from_email='cyberbudy@gmail.com',
                    recipients=['cyberbudy@gmail.com'],
                    context={},
                    language='asd'
                )

    def test_mail_without_parler_settings(self):
        with self.settings(
            POSTIE_TEMPLATE_CHOICES=self.new_events,
            POSTIE_INSTANT_SEND=True,
            PARLER_LANGUAGES={},
            LANGUAGES=(('en', 'EN'),),
            LANGUAGE_CODE='en'
        ):
            template = G(
                Template,
                name='event',
                event='event',
                subject='Subject',
                html='<b>Mail body</b>',
                plain='Mail body',
            )
            template.subject = 'Subject'
            template.save()

            send_mail(
                event='event',
                from_email='cyberbudy@gmail.com',
                recipients=['cyberbudy@gmail.com'],
                context={}
            )
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'Subject')

    def test_mail_with_translated_language(self):
        with self.settings(
            POSTIE_TEMPLATE_CHOICES=self.new_events,
            POSTIE_INSTANT_SEND=True,
        ):
            template = G(
                Template,
                name='event',
                event='event',
                subject='Subject',
                html='<b>Mail body</b>',
                plain='Mail body',
            )
            template.set_current_language('en')
            template.subject = 'Test Subject 1'
            template.html = 'Test html 1'
            template.plain = 'Test plain 1'
            template.save()

            send_mail(
                event='event',
                from_email='cyberbudy@gmail.com',
                recipients=['cyberbudy@gmail.com'],
                context={}
            )

            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, 'Test Subject 1')
