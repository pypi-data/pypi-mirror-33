from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from model_utils import Choices


__all__ = (
    'LETTER_STATUSES',
    'EVENTS',
    'POSTIE_TEMPLATE_CONTEXTS'
)


LETTER_STATUSES = Choices(
    ('draft', _('draft')),
    ('sent', _('Sent')),
    ('failed', _('Failed'))
)

EVENTS = getattr(settings, 'POSTIE_TEMPLATE_CHOICES', [])
POSTIE_TEMPLATE_CONTEXTS = getattr(settings, 'POSTIE_TEMPLATE_CONTEXTS', {})
