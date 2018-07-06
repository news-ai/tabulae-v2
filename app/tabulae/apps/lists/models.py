# -*- coding: utf-8 -*-
# Core Django imports
from django.db import models

# Third-party app imports
from taggit.managers import TaggableManager

# Imports from app
from tabulae.apps.general.models import BaseModel


class CustomFieldsMap(BaseModel):
    name = models.TextField(blank=True, default='')
    value = models.TextField(blank=True, default='')
    custom_field = models.BooleanField(blank=True, default=False)
    hidden = models.BooleanField(blank=True, default=False)

    # The order of each of the custom fields
    order = models.IntegerField(blank=True, default=50)

    class Meta:
        ordering = ('order',)


class MediaList(BaseModel):
    name = models.TextField(blank=True, default='')
    client_name = models.TextField(blank=True, default='')
    clients = models.ManyToManyField(
        'users.Client', blank=True, related_name='+')

    contacts = models.ManyToManyField(
        'contacts.Contact', blank=True, related_name='+')

    fields_map = models.ManyToManyField(
        CustomFieldsMap, blank=True, related_name='+')

    tags = TaggableManager(blank=True)

    file = models.ForeignKey('files.File', blank=True,
                             null=True, related_name='+')

    team = models.ForeignKey('users.Team', blank=True,
                             null=True, related_name='+')

    # read_only = models.BooleanField(blank=False, default=False)
    public_list = models.BooleanField(blank=True, default=False)
    archived = models.BooleanField(blank=True, default=False)
    subscribed = models.BooleanField(blank=True, default=False)

    is_deleted = models.BooleanField(blank=True, default=False)

    class Meta:
        verbose_name_plural = "medialists"

    def __unicode__(self):
        return self.name
