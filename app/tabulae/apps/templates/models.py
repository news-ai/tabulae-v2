# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Imports from app
from tabulae.apps.general.models import BaseModel


class Template(BaseModel):
    name = models.TextField(blank=True, default='')
    subject = models.TextField(blank=True, default='')
    body = models.TextField(blank=True, default='')

    archived = models.BooleanField(blank=True, default=False)
