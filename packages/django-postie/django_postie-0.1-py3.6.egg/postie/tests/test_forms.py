from decimal import Decimal

from django import test, forms

from ..forms import MailSendFormMixin

__all__ = (
    'MailSendFormMixinTestCase'
)


class TestForm(forms.Form, MailSendFormMixin):
    char_field = forms.CharField()
    decimal_field = forms.DecimalField()
    choices_field = forms.ChoiceField(
        choices=(
            (1, 'first'),
            (2, 'second'),
            (3, 'third'),
        )
    )


class MailSendFormMixinTestCase(test.TestCase):
    def test_get_email_event(self):
        form = MailSendFormMixin()
        self.assertEqual(form.get_email_template(), None)

        form.email_template = 'event'

        self.assertEqual(form.get_email_template(), 'event')

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
    #
    # def test_get_email_extra_data(self):
    #     form = MailSendFormMixin()
    #
    #     self.assertEqual(
    #         form.get_email_extra_data(),
    #         {
    #             'cc': [],
    #             'bcc': [],
    #             'reply_to': [],
    #             'headers': {}
    #         }
    #     )

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
