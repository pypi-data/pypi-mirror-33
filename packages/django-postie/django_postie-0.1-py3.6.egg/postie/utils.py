from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache


__all__ = (
    'get_protocol',
    'get_domain',
    'decode_list',
    'encode_list',
)


def get_protocol():
    """
    Returns data transfer protocol name.
    The value is determined by bool variable 'USE_HTTPS' in settings.

    Returns:
        str: 'https' if 'USE_HTTPS' is True, otherwise - 'http'.
    """
    return 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'


def get_domain(request=None):
    """
    Returns domain name this site.

    Args:
        request (HttpRequest): Request.

    Returns:
        str: Domain name.
    """
    site_name = cache.get('site_name')

    if site_name is None:
        site_name = Site.objects.get_current(request).domain

        cache.set(
            'site_name', site_name,
            getattr(settings, 'PREFERENCES_CACHE_TTL', 60 * 10)
        )

    return site_name


def decode_list(string):
    return string.split(',')


def encode_list(_list):
    return ','.join(_list)
