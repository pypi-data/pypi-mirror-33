from django import test

from ..entities import Template
from ..models import Template as TemplateModel

__all__ = (
    'TemplateEntityTestCase',
)


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
