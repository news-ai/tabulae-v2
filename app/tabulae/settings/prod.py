# -*- coding: utf-8 -*-
# Imports from app
from tabulae.settings.common import *
import secrets

# Third-party app imports
import raven

DEBUG = False

ALLOWED_HOSTS = [
    'api.newsai.org',
    '13.58.42.148',
    'tabulae.newsai.com'
]

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'drf_ujson.renderers.UJSONRenderer',
)

REST_FRAMEWORK['DEFAULT_PARSER_CLASSES'] = (
    'drf_ujson.parsers.UJSONParser',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'api',
        'USER': 'newsaiapitest',
        'PASSWORD': '*Q4MQNCbtlLyP',
        'HOST': 'newsaiapitest.cnloofuhvjcp.us-east-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            'redis://tabulae-django-1.nd1tz4.0001.use2.cache.amazonaws.com:6379'
        ],
        'OPTIONS': {
            'DB': 0,
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        },
    },
}

CORS_ORIGIN_WHITELIST = (
    'localhost:8000',
    'localhost:3000',
    'tabulae.newsai.com'
)

CORS_ALLOW_CREDENTIALS = True
CORS_REPLACE_HTTPS_REFERER = True

# Social Auth
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

# Swagger
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# write session information to the database and only load it from the cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Email settings
DEFAULT_FROM_EMAIL = 'Abhi from NewsAI <abhi@newsai.co>'
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = secrets.NEWSAI_SENDGRID_API_KEY
SENDGRID_SANDBOX_MODE_IN_DEBUG = False

# Celery
BROKER_URL = 'redis://tabulae-django-1.nd1tz4.0001.use2.cache.amazonaws.com:6379/0'
CELERY_RESULT_BACKEND = 'redis://tabulae-django-1.nd1tz4.0001.use2.cache.amazonaws.com:6379'
CELERYD_CONCURRENCY = 4

# Raven for logging
RAVEN_CONFIG = {
    'dsn': 'https://' + secrets.SENTRY_USERNAME + ':' + secrets.SENTRY_PASSWORD
    + '@app.getsentry.com/' + secrets.SENTRY_ACCOUNTID,
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.path.dirname(BASE_DIR))),
}

SWAGGER_SETTINGS = {
    'is_superuser': True
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry', 'SysLog'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s NewsAI API: %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'SysLog': {
            'level': 'DEBUG',
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'simple',
            'address': ('logs6.papertrailapp.com', 21890)
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'SysLog'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'SysLog'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django': {
            'handlers': ['console', 'SysLog'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console', 'SysLog'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console', 'SysLog'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console', 'SysLog'],
            'propagate': False,
        },
    },
}

DATADOG_TRACE = {
    'DEFAULT_SERVICE': 'newsai-api',
    'TAGS': {'env': 'production'},
}