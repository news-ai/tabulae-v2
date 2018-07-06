# Stdlib imports
from __future__ import absolute_import

# Imports from app
from .celery import app as celery_app

__all__ = ['celery_app']
