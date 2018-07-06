#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Stdlib imports
import os
import sys

from gevent import monkey
monkey.patch_all()

from psycogreen.gevent import patch_psycopg
patch_psycopg()

if __name__ == "__main__":
    env = os.getenv('TABULAE_ENVIRONMENT') or 'dev'
    if env not in ('dev', 'stage', 'prod', 'test'):
        env = 'dev'
    os.environ.setdefault("TABULAE_ENVIRONMENT", env)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                          "tabulae.settings.%s" % env)
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
