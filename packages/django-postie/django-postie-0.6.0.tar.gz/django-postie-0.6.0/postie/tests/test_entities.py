from unittest.mock import patch

from django import test
from django.conf import settings
from django.core import mail

from django_dynamic_fixture import G

from ..entities import Template, Letter
from ..models import (
    Template as TemplateModel, Letter as LetterModel
)

__all__ = (
    'TemplateEntityTestCase',
)


class TestBackend:
    def send(self, letter):
        letter.message.send()


class TemplateEntityTestCase(test.TestCase):

    def test_render_template_method(self):
        template = TemplateModel(
            event='event',
            name='template',
            subject='Test {{ subject_var }} {{ global_var }}',
            html='Test {{ body_var }} {{ global_var }}',
            plain='Test {{ txt_var }} {{ global_var }}'
        )
        entity = Template(template)
        rendered = entity.render(
            {
                'subject_var': 'subject', 'global_var': 'global',
                'body_var': 'body', 'txt_var': 'txt'
            }
        )
        self.assertEqual(rendered.get('subject'), 'Test subject global')
        self.assertEqual(rendered.get('html'), 'Test body global')
        self.assertEqual(rendered.get('plain'), 'Test txt global')

    def test_from_event_method(self):
        template = TemplateModel.objects.create(
            event='event',
            name='template',
            subject='Test {{ subject_var }} {{ global_var }}',
            html='Test {{ body_var }} {{ global_var }}',
            plain='Test {{ txt_var }} {{ global_var }}'
        )

        entity = Template.from_event('event')
        self.assertIsInstance(entity, Template)
        self.assertEqual(entity.object, template)

    def test_legend(self):
        legend = '\n'.join(
            f'{{{{ {key} }}}}: {value}'
            for key, value in
            settings.POSTIE_TEMPLATE_CONTEXTS.get('1', {}).items()
        )
        G(TemplateModel, event='1')

        entity = Template(TemplateModel.objects.get(event='1'))

        self.assertEqual(legend, entity.legend)

    def test_new_letter(self):
        template = G(TemplateModel, event='1')
        template.set_current_language('en')
        template.subject = 'Test subject {{var1}}'
        template.html = 'Test'
        template.plain = 'Test'
        template.save()

        entity = Template(template)

        letter_entity = entity.new_letter(
            context={'var1': 'var 1', 'var2': 'var 2'},
            recipients=['test@test.test'],
            email_from='asd@asd.asd'
        )

        self.assertEqual(letter_entity.object.subject, 'Test subject var 1')

    def test_new_letter_without_email_from(self):
        template = G(TemplateModel, event='1')
        entity = Template(template)

        letter_entity = entity.new_letter(
            context={'var1': 'var 1', 'var2': 'var 2'},
            recipients=['test@test.test'],
        )

        self.assertEqual(
            letter_entity.object.email_from, settings.DEFAULT_FROM_EMAIL
        )

    def test_send(self):
        letter = G(LetterModel)

        # No usecase
        with self.settings(POSTIE_INSTANT_SEND=True):
            Letter(letter).send()
            self.assertEqual(len(mail.outbox), 1)

        # Celery email backend
        with self.settings(POSTIE_INSTANT_SEND=False):
            with patch('postie.tasks.send_letter.delay'):
                Letter(letter).send()
                self.assertEqual(len(mail.outbox), 1)

        # TestBackend
        Letter(letter).send(TestBackend)
        self.assertEqual(len(mail.outbox), 2)
