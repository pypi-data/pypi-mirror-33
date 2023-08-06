from typing import Dict

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.translation import activate
from django.db import transaction

from postie.models import Template
from postie.const import POSTIE_TEMPLATE_CONTEXTS


class Command(BaseCommand):
    help = 'Creates templates that are not created'

    @transaction.atomic
    def handle(self, *args, **options):
        templates = Template.objects.all().values_list('event', flat=True)
        created = 0

        for event, context in POSTIE_TEMPLATE_CONTEXTS.items():
            if event in templates:
                continue

            self.create_blank_template(event, context)

            created += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created} templates'))

    def create_blank_template(self, event: str, context: Dict):
        activate(settings.LANGUAGE_CODE)
        template_context = self.generate_template(event, context)

        template = Template.objects.create(**template_context)

        for code, verbose in settings.LANGUAGES:
            template.set_current_language(code)

            for field, value in template_context.items():
                setattr(template, field, value)

            template.save()

    def generate_template(self, event: str, context: Dict) -> Dict:
        vars = '<br>'.join(
            f'{{{{ {key} }}}}: {value}' for key, value in context.items()
        )

        return {
            'name': event.title().replace('_', ' '),
            'subject': event.title().replace('_', ' '),
            'html': f'<html><body>{vars}</body></html>',
            'plain': vars,
            'event': event,
        }
