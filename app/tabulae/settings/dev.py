# -*- coding: utf-8 -*-
# Imports from app
from tabulae.settings.common import *
import secrets

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

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

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
)

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    },
}

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    'localhost:8000',
    'localhost:3000',
)

# Email server
DEFAULT_FROM_EMAIL = 'Abhi from NewsAI <abhi@newsai.co>'
EMAIL_BACKEND = 'sendgrid_backend.SendgridBackend'
SENDGRID_API_KEY = secrets.NEWSAI_SENDGRID_API_KEY

# write session information to the database and only load it from the cache
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# Celery Settings
BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# Stripe Settings
STRIPE_LIVE_MODE = True

DATADOG_TRACE = {
    'DEFAULT_SERVICE': 'newsai-api',
    'TAGS': {'env': 'development'},
}