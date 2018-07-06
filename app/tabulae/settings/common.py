# -*- coding: utf-8 -*-
# Stdlib imports
import datetime
import os
from logging.handlers import SysLogHandler

# Third-party app imports
from kombu import Queue

# Imports from app
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '*+j6z(8wbsfon8x^mv56d4xmg8*nx-4grs1)^u9tu!#__2g%f='
DEBUG = True
APPEND_SLASH = True
ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_extensions',
    'django_countries',
    'corsheaders',
    'raven.contrib.django.raven_compat',
    'rest_framework_swagger',
    'taggit',
    'taggit_serializer',
    'storages',
    'djstripe',
    'cachalot',
    'tabulae',
    'tabulae.apps.users',
    'tabulae.apps.publications',
    'tabulae.apps.lists',
    'tabulae.apps.contacts',
    'tabulae.apps.files',
    'tabulae.apps.emails',
    'tabulae.apps.templates',
    'tabulae.apps.feeds',
    'tabulae.apps.database_contacts',
    'tabulae.apps.database_publications',
    'ddtrace.contrib.django',
)

AUTH_USER_MODEL = 'tabulae.User'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = secrets.NEWSAI_GOOGLE_OAUTH2_CLIENT_ID
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = secrets.NEWSAI_GOOGLE_OAUTH2_CLIENT_SECRET
SOCIAL_AUTH_LOGIN_REDIRECT_URL = secrets.SOCIAL_AUTH_LOGIN_REDIRECT_URL
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = secrets.SOCIAL_AUTH_NEW_USER_REDIRECT_URL

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
    'tabulae.apps.users.utils.check_agency_auth_google_auth',
)

ACCOUNT_ACTIVATION_DAYS = 30

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'tabulae.apps.users.utils.EmailBackend',
)

# S3
AWS_ACCESS_KEY_ID = secrets.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = secrets.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = secrets.AWS_STORAGE_BUCKET_NAME
AWS_QUERYSTRING_AUTH = False
AWS_HEADERS = {
    'Cache-Control': 'max-age=86400',
}
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_CUSTOM_DOMAIN = 's3.amazonaws.com/%s' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/" % (AWS_S3_CUSTOM_DOMAIN)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'tabulae.middleware.disable_csrf',
)

ROOT_URLCONF = 'tabulae.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'tabulae.wsgi.application'

# Stripe Settings
STRIPE_LIVE_PUBLIC_KEY = secrets.STRIPE_LIVE_PUBLIC_KEY
STRIPE_LIVE_SECRET_KEY = secrets.STRIPE_LIVE_SECRET_KEY
STRIPE_TEST_PUBLIC_KEY = secrets.STRIPE_TEST_PUBLIC_KEY
STRIPE_TEST_SECRET_KEY = secrets.STRIPE_TEST_SECRET_KEY
STRIPE_LIVE_MODE = True

# Celery
CELERY_REDIS_MAX_CONNECTIONS = 1
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_IGNORE_RESULT = True
CELERYD_TASK_SOFT_TIME_LIMIT = 60

# Sensible settings for celery
CELERY_ALWAYS_EAGER = False
CELERY_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False

# By default we will ignore result
# If you want to see results and try out tasks interactively, change it to False
# Or change this setting on tasks level
CELERY_IGNORE_RESULT = True
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_TASK_RESULT_EXPIRES = 600

# Specific celery
CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 1000

# Having a started state can be useful for when there are long running
# tasks and there is a need to report which task is currently running.
CELERY_TRACK_STARTED = True

# The worker processing the task will be killed and replaced with a new
# one when this is exceeded.
CELERYD_TASK_TIME_LIMIT = 60 * 30

# Tasks can be tracked before they are consumed by a worker.
CELERY_SEND_TASK_SENT_EVENT = True

CELERY_QUEUES = (
    Queue('default'),
    Queue('emails'),
)

# Cache
CACHALOT_ENABLED = True

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

TABULAE_FORMAT_KEYS = 'camelize'

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'tabulae.apps.general.exceptions.exception_handler',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'tabulae.apps.general.pagination.GlobalPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_ETAG_FUNC': 'rest_framework_extensions.utils.default_etag_func',
    'ORDERING_PARAM': 'order',
}
