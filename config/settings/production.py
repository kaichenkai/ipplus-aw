"""
Production settings for ipplus project.


- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis for cache

- Use sentry for error logging


"""

import logging

from .base import *  # noqa

# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# raven sentry client
# See https://docs.sentry.io/clients/python/integrations/django/


# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/middleware/#module-django.middleware.security
# and https://docs.djangoproject.com/en/dev/howto/deployment/checklist/#run-manage-py-check-deploy

# set this to 60 seconds and then to 518400 when you can prove it works
# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
#     'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
# SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
#     'DJANGO_SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = True
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
# SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
# CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
# X_FRAME_OPTIONS = 'DENY'

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['api.seebug.org', ])
# END SITE CONFIGURATION

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s[%(lineno)d] %(message)s"
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', ],
            'propagate': False,
        },
        "sentry_sdk": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'scrapy': {
            'level': 'ERROR',
            'handlers': ['console', ],
            'propagate': False,
        },
        'elasticsearch': {
            'level': 'ERROR',
            'handlers': ['console', ],
            'propagate': False,
        },
    },
    "root": {"level": "INFO", "handlers": ['console']},
}

# Sentry Configuration
SENTRY_DSN = env('DJANGO_SENTRY_DSN', default='http://user:admin@183.60.243.205/sentry/28')
SENTRY_LOG_LEVEL = env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO)

if SENTRY_DSN:
    import logging
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from ipplus import __version__

    print('Loading sentry sdk')

    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment="production",
        integrations=[sentry_logging, DjangoIntegration(), CeleryIntegration()],
        release=__version__,
    )

# Your production stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
PROJECT_OPTIONS = {
    'system.url-prefix': 'https://ti.darkeye.site',
}

# SESSION_COOKIE_DOMAIN = 'darkeye.site'
# SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_HTTPONLY = True
