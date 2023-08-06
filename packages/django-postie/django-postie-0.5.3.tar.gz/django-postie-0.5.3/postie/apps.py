from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PostieConfig(AppConfig):
    name = 'postie'
    verbose_name = _('Postie')
