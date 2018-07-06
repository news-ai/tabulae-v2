# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Imports from app
from tabulae.models import User
from tabulae.apps.general.models import BaseModel


class Feed(BaseModel):
    feed_url = models.TextField(blank=True, default='')

    contact = models.ForeignKey('contacts.Contact', blank=True,
                                null=True, related_name='+')
    publication = models.ForeignKey(
        'publications.Publication', blank=True,
        null=True, related_name='+')

    valid_feed = models.BooleanField(blank=True, default=False)
    running = models.BooleanField(blank=True, default=False)

    class Meta:
        verbose_name_plural = "feeds"

    def __unicode__(self):
        return self.feed_url
