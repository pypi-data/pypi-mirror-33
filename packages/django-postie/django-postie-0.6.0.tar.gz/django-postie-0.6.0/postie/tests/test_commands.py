from django import test
from django.core.management import call_command

from django_dynamic_fixture import G

from ..models import Template
from postie import const


class TestCreateTemplatesCommandTestCase(test.TestCase):
    def test_command(self):
        contexts = {
            '1': {
                'var1': 'desc',
                'var2': 'desc 1',
                'var3': 'desc 2'
            },
            '2': {
                'var1': 'desc',
                'var2': 'desc 1',
                'var3': 'desc 2'
            },
        }
        Template.objects.all().delete()

        const.POSTIE_TEMPLATE_CONTEXTS = contexts

        self.assertEqual(Template.objects.count(), 0)
        call_command('create_templates')
        self.assertEqual(Template.objects.count(), 2)

    def test_command_already_created_templates(self):
        contexts = {
            '1': {
                'var1': 'desc',
                'var2': 'desc 1',
                'var3': 'desc 2'
            },
            '2': {
                'var1': 'desc',
                'var2': 'desc 1',
                'var3': 'desc 2'
            },
        }
        Template.objects.all().delete()
        G(Template, event='1')

        const.POSTIE_TEMPLATE_CONTEXTS = contexts

        self.assertEqual(Template.objects.count(), 1)
        call_command('create_templates')
        self.assertEqual(Template.objects.count(), 2)
