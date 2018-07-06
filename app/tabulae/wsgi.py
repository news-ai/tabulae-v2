"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

# -*- coding: utf-8 -*-
# Stdlib imports
import os

# Core Django imports
from django.core.wsgi import get_wsgi_application

env = os.getenv('TABULAE_ENVIRONMENT') or 'dev'
if env not in ('dev', 'stage', 'prod'):
    env = 'dev'
os.environ.setdefault("TABULAE_ENVIRONMENT", env)
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "tabulae.settings.%s" % env)
application = get_wsgi_application()
