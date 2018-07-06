# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Imports from app
from tabulae.apps.general.models import BaseModel


class Publication(BaseModel):
    name = models.TextField(blank=True, default='', unique=True)
    url = models.URLField(blank=True, default='', unique=True)

    linkedin = models.TextField(blank=True, default='')
    twitter = models.TextField(blank=True, default='')
    instagram = models.TextField(blank=True, default='')
    websites = ArrayField(models.CharField(
        max_length=200), blank=True, default=list)
    blog = models.TextField(blank=True, default='')

    verified = models.BooleanField(blank=True, default=False)
