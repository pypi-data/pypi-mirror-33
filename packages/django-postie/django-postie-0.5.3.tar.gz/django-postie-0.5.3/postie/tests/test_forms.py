from decimal import Decimal

from django import test, forms
from django.core import mail

from django_dynamic_fixture import G

from ..forms import MailSendFormMixin
from ..models import Template

__all__ = (
    'MailSendFormMixinTestCase'
)


class TestForm(MailSendFormMixin, forms.Form):
    char_field = forms.CharField()
    decimal_field = forms.DecimalField()
    choices_field = forms.ChoiceField(
        choices=(
            (1, 'first'),
            (2, 'second'),
            (3, 'third'),
        )
    )

    def get_email_recipients(self):
        return ['test@test.test']


# Emulate model form
class SaveForm(forms.Form):
    def save(self, commit=True):
        return 'object is saved'
    

class TestSaveForm(TestForm, SaveForm):
    char_field = forms.CharField()
    decimal_field = forms.DecimalField()
    choices_field = forms.ChoiceField(
        choices=(
            (1, 'first'),
            (2, 'second'),
            (3, 'third'),
        )
    )
    
    def get_email_recipients(self):
        return ['test@test.test']


class MailSendFormMixinTestCase(test.TestCase):
    def test_get_email_event(self):
        form = MailSendFormMixin()
        self.assertEqual(form.get_email_template_event(), None)

        form.email_template_event = 'event'

        self.assertEqual(form.get_email_template_event(), 'event')

    def test_get_email_sender(self):
        form = MailSendFormMixin()

        with self.settings(DEFAULT_FROM_EMAIL='admin@admin.com'):
            self.assertEqual(
                form.get_email_sender(), 'admin@admin.com'
            )

    def test_get_email_recipients(self):
        form = MailSendFormMixin()

        with self.assertRaises(NotImplementedError):
            form.get_email_recipients()

    def test_get_email_context(self):
        form = TestForm(data={
            'char_field': 'char data',
            'decimal_field': Decimal(12.033),
            'choices_field': 1,
        })

        # Form should be validated first, before the context retrieving.
        with self.assertRaises(AttributeError):
            form.get_email_context()

        form.is_valid()

        self.assertEqual(
            form.get_email_context(),
            {
                'char_field': 'char data',
                'choices_field': '1',
                'decimal_field': str(Decimal(12.033))
            }
        )

    def test_send_email(self):
        template = G(Template)
        form = TestForm(data={
            'char_field'   : 'char data',
            'decimal_field': Decimal(12.033),
            'choices_field': 1,
        })

        form.email_template_event = template.event
        form.is_valid()
        form.send_email()

        self.assertEqual(len(mail.outbox), 1)

    def test_save(self):
        # Test the form without save method is sending the email
        template = G(Template)
        form = TestForm(data={
            'char_field'   : 'char data',
            'decimal_field': Decimal(12.033),
            'choices_field': 1,
        })

        form.email_template_event = template.event
        form.is_valid()
        form.save()

        self.assertEqual(len(mail.outbox), 1)

    def test_save_implemented(self):
        # Test the form with save method is sending the email

        template = G(Template)
        form = TestSaveForm(data={
            'char_field'   : 'char data',
            'decimal_field': Decimal(12.033),
            'choices_field': 1,
        })

        form.email_template_event = template.event
        form.is_valid()
        response = form.save()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(response, 'object is saved')
