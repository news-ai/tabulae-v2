# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Third-party app imports
from taggit.managers import TaggableManager

# Imports from app
from tabulae.apps.general.models import BaseModel


class CustomContactField(BaseModel):
    name = models.TextField(blank=True, default='')
    value = models.TextField(blank=True, default='')


class Contact(BaseModel):
    first_name = models.TextField(blank=True, default='')
    last_name = models.TextField(blank=True, default='')
    email = models.EmailField(blank=True, max_length=254)

    notes = models.TextField(blank=True, default='')

    employers = models.ManyToManyField(
        'publications.Publication', blank=True, related_name='+')
    past_employers = models.ManyToManyField(
        'publications.Publication', blank=True, related_name='+')

    linkedin = models.TextField(blank=True, default='')
    twitter = models.TextField(blank=True, default='')
    instagram = models.TextField(blank=True, default='')
    websites = ArrayField(models.CharField(
        max_length=200), blank=True, default=list)
    blog = models.TextField(blank=True, default='')

    twitter_invalid = models.BooleanField(blank=True, default=False)
    instagram_invalid = models.BooleanField(blank=True, default=False)

    twitter_private = models.BooleanField(blank=True, default=False)
    instagram_private = models.BooleanField(blank=True, default=False)

    location = models.TextField(blank=True, default='')
    phone_number = models.TextField(blank=True, default='')

    custom_fields = models.ManyToManyField(
        CustomContactField, blank=True, related_name='+')

    is_outdated = models.BooleanField(blank=True, default=False)
    email_bounced = models.BooleanField(blank=True, default=False)

    is_master_contact = models.BooleanField(blank=True, default=False)
    is_deleted = models.BooleanField(blank=True, default=False)

    tags = TaggableManager(blank=True)

    team = models.ForeignKey(
        'users.Team', related_name='+', null=True, blank=True)
    client = models.ForeignKey(
        'users.Client', related_name='+', null=True, blank=True)

    linkedin_updated = models.DateTimeField(auto_now=True, editable=True)

    class Meta:
        verbose_name_plural = 'contacts'

    def verify_email(self):
        pass

    def enhance_contact(self):
        pass
