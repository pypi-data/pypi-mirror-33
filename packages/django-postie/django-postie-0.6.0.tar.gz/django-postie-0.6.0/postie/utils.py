from typing import List

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.handlers.wsgi import WSGIRequest

__all__ = (
    'get_protocol',
    'get_domain',
    'to_list',
    'to_str',
    'default_language'
)


def get_protocol() -> str:
    """
    Returns data transfer protocol name.
    The value is determined by bool variable 'USE_HTTPS' in settings.

    Returns:
        str: 'https' if 'USE_HTTPS' is True, otherwise - 'http'.
    """

    return 'https' if getattr(settings, 'USE_HTTPS', False) else 'http'


def get_domain(request: WSGIRequest=None) -> str:
    """
    Returns domain name this site.

    Args:
        request (WSGIRequest): Request.

    Returns:
        str: Domain name.
    """

    site_name = Site.objects.get_current(request).domain

    return site_name


def to_list(string: str) -> List[str]:
    """
    Transforms string to list.

    Args:
        string (str): String to transform.

    Returns:
        List[str]: List
    """

    return string.split(',')


def to_str(_list: List[str]) -> str:
    """
    Transforms list to str.

    Args:
        _list (List[str]): List to transform to str

    Returns:
        str: Transformed list
    """

    return ','.join(_list)


def default_language() -> str:
    """
    Returns default site language.

    Returns:
        str: Default site language
    """
    if hasattr(settings, 'PARLER_LANGUAGES') and settings.PARLER_LANGUAGES:
        return (
            settings.PARLER_LANGUAGES.get('default', {}).get('fallback')
        )
    else:
        return settings.LANGUAGE_CODE
