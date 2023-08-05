from django.conf import settings
from django.core.checks import Warning, register


@register()
def check_installed_apps(app_configs, **kwargs):
    if 'django.contrib.postgres' not in settings.INSTALLED_APPS:
        return [
            Warning(
                'django.contrib.postgres is not included in INSTALLED_APPS. '
                'This is required for Postgres full text search.',
                hint='add django.contrib.postgres to INSTALLED_APPS',
                id='bomojo.W001',
            )
        ]

    return []
