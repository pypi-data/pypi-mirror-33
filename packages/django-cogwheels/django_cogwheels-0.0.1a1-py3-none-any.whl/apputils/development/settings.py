"""
Example settings for local development

Use this file as a base for your local development settings and copy
it to setting.py. It should not be checked into your code repository.
"""
from apputils.tests.settings import *  # noqa

DEBUG = True

DATABASES = {
    'default': {
        'NAME': 'dev-db.sqlite',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS += (
    'django_extensions',
    'apputils.development',
)


ROOT_URLCONF = 'apputils.development.urls'
INTERNAL_IPS = ['127.0.0.1']


# =============================================================================
# Paths
# =============================================================================

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'development', 'staticfiles')
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'development', 'media')
