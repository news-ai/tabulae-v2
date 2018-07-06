# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Imports from app
from tabulae.apps.general.models import BaseModel


class DatabasePublication(BaseModel):
	short_id = models.TextField(blank=True, default='')

	name = models.TextField(blank=True, default='')
	url = models.TextField(blank=True, default='')

	class Meta:
		verbose_name_plural = 'database-publications'
