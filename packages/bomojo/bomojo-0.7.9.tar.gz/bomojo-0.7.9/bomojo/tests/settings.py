import os

import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'test-secret-key'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.postgres',
    'bomojo.movies',
    'bomojo.matchups',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'bomojo.middleware.JSONMiddleware',
]

# Tests extend the default URL config to expose a login endpoint.
ROOT_URLCONF = 'bomojo.urls'

DATABASES = {
    'default': dj_database_url.config(
        default='postgres://postgres@127.0.0.1:5432/bomojo_test')
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

MEDIA_ROOT = os.path.join(BASE_DIR, 'tests', 'data')
MEDIA_URL = '/media/'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
