# -*- coding: utf-8 -*-
# Stdlib imports
from __future__ import absolute_import
import os

# Core Django imports
from django.conf import settings

# Third-party app imports
from celery import Celery

env = os.getenv('TABULAE_ENVIRONMENT') or 'dev'
if env not in ('dev', 'stage', 'prod'):
    env = 'dev'
os.environ.setdefault("TABULAE_ENVIRONMENT", env)
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "tabulae.settings.%s" % env)

app = Celery('tabulae')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
