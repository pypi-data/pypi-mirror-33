from pathlib import Path

from django.utils.translation import ugettext_lazy as _

from model_utils import Choices


BASE_DIR = Path('..')
BASE_ROOT = BASE_DIR / '..'

SECRET_KEY = '!SECRET_KEY!'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = True

ROOT_URLCONF = 'postie.tests.urls'

INSTALLED_APPS = (
    'postie',
    'codemirror2',
    'ckeditor',
    'parler',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.staticfiles',
)

MIDDLEWARE = MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': (
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            )
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3'
    }
}

TIME_ZONE = 'UTC'
LANGUAGE_CODE = 'en'
USE_I18N = True
USE_L10N = True

SITE_ID = 1

STATIC_URL = '/static/'
STATIC_ROOT = BASE_ROOT / 'static'
MEDIA_URL = '/uploads/'
MEDIA_ROOT = BASE_ROOT / 'uploads'


POSTIE_TEMPLATE_CHOICES = Choices(
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
)

POSTIE_TEMPLATE_CONTEXTS = {
    '1': {
        'var1': 'desc',
        'var2': 'desc1',
        'var3': 'desc2'
    }
}

POSTIE_INSTANT_SEND = True


PARLER_LANGUAGES = {
    1: (
        {'code': 'en', },
        {'code': 'en-us', },
        {'code': 'it', },
        {'code': 'nl', },
    ),
    'default': {
        'fallback': 'en',             # defaults to PARLER_DEFAULT_LANGUAGE_CODE
        # the default; let .active_translations() return fallbacks too.
        'hide_untranslated': False,
    }
}

LANGUAGES = (
    ('en', _("English")),
    ('en-us', _("US English")),
    ('it', _('Italian')),
    ('nl', _('Dutch')),
    ('fr', _('French')),
    ('es', _('Spanish')),
)

LOCALE_PATH = [
    Path(__file__).parent.parent / 'locale'
]
