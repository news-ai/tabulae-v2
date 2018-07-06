# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Third-party app imports
from taggit.managers import TaggableManager
import moneyed
from djmoney.models.fields import MoneyField

# Imports from app
from tabulae.models import User
from tabulae.apps.general.models import BaseModel


# Django Models
class Billing(BaseModel):
    stripe_id = models.TextField(blank=True, default='')
    stripe_plan_id = models.TextField(blank=True, default='')

    has_trial = models.BooleanField(blank=True, default=False)
    is_on_trial = models.BooleanField(blank=True, default=False)
    is_agency = models.BooleanField(blank=True, default=False)
    is_cancel = models.BooleanField(blank=True, default=False)

    expires = models.DateTimeField(auto_now=True, editable=True)

    class Meta:
        verbose_name_plural = "billings"

    def __unicode__(self):
        return self.stripe_id


class EmailCode(BaseModel):
    invite_code = models.TextField(blank=False, default='')
    email = models.EmailField(max_length=254)

    class Meta:
        verbose_name_plural = "email-codes"

    def __unicode__(self):
        return self.email


class Invite(BaseModel):
    invite_code = models.TextField(blank=False, default='')
    email = models.EmailField(max_length=254, unique=True)
    is_used = models.BooleanField(blank=False, default=False)

    class Meta:
        verbose_name_plural = "invites"

    def __unicode__(self):
        return self.invite_code, self.email


class Agency(BaseModel):
    name = models.TextField(blank=False, default='')
    email = models.TextField(blank=False, default='')
    administrators = models.ManyToManyField(
        User, blank=False, related_name='+')

    class Meta:
        verbose_name_plural = "agencies"

    def __unicode__(self):
        return self.name


class Client(BaseModel):
    name = models.TextField(blank=True, default='')
    url = models.URLField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    tags = TaggableManager()

    agency = models.ForeignKey(Agency)

    linkedin = models.TextField(blank=True, default='')
    twitter = models.TextField(blank=True, default='')
    instagram = models.TextField(blank=True, default='')
    websites = ArrayField(models.CharField(
        max_length=200), blank=True, default=list)
    blog = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = "clients"

    def __unicode__(self):
        return self.name


class Team(BaseModel):
    name = models.TextField(blank=True, default='')
    agency = models.ForeignKey(Agency)
    max_members = models.IntegerField(blank=True, default=0)
    members = models.ManyToManyField(User, blank=True, related_name='+')
    admins = models.ManyToManyField(User, blank=True, related_name='+')

    class Meta:
        verbose_name_plural = "teams"

    def __unicode__(self):
        return self.name


class UserProfile(BaseModel):
    user = models.OneToOneField(User, related_name='+')

    # Google Id generated for a particular user
    google_id = models.TextField(blank=True, default='')

    # Billing
    billing = models.OneToOneField(
        Billing, related_name='+', blank=True, null=True)

    # Email configuration
    sendgrid_emails = ArrayField(models.CharField(
        max_length=200), blank=True, default=list)
    email_alias = models.TextField(blank=True, default='')

    # API Key generated for each user
    api_key = models.TextField(blank=True, default='')

    # Employers
    employers = models.ManyToManyField(Agency, blank=True, related_name='+')
    team = models.ForeignKey(Team, blank=True, null=True, related_name='+')

    # Account settings
    email_confirmed = models.BooleanField(blank=True, default=False)
    get_daily_emails = models.BooleanField(blank=True, default=False)

    # Email Signature
    email_signature = models.TextField(blank=True, default='')
    email_signatures = ArrayField(models.TextField(
        blank=True), blank=True, default=list)

    live_access_token = models.TextField(blank=True, default='')

    # Gmail settings
    gmail = models.BooleanField(blank=True, default=False)
    gmail_username = models.TextField(blank=True, default='')
    gmail_token_type = models.TextField(blank=True, default='')
    gmail_expires_in = models.DateTimeField(auto_now=True, editable=True)
    gmail_refresh_token = models.TextField(blank=True, default='')
    gmail_access_token = models.TextField(blank=True, default='')
    gmail_google_code = models.TextField(blank=True, default='')

    # Gmail Nylas
    gmail_nylas_code = models.TextField(blank=True, default='')
    gmail_nylas_access_token = models.TextField(blank=True, default='')

    # Outlook Nylas
    outlook = models.BooleanField(blank=True, default=False)
    outlook_username = models.TextField(blank=True, default='')
    outlook_token_type = models.TextField(blank=True, default='')
    outlook_access_token = models.TextField(blank=True, default='')
    outlook_microsoft_code = models.TextField(blank=True, default='')
    outlook_email_provider = models.TextField(blank=True, default='')

    # Other Nylas
    external_email = models.BooleanField(blank=True, default=False)
    external_email_username = models.TextField(blank=True, default='')
    external_email_access_token = models.TextField(blank=True, default='')
    external_email_token_type = models.TextField(blank=True, default='')
    external_email_account_id = models.TextField(blank=True, default='')
    external_email_provider = models.TextField(blank=True, default='')

    trial_feedback = models.BooleanField(blank=True, default=False)
    trial_expire_reason = models.TextField(blank=True, default='')
    trial_expire_feedback = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = "user-profiles"

    def __unicode__(self):
        return self.user.email

    def get_user_email_provider(self):
    	provider = ''
    	if self.gmail is True:
    	    provider = 'gmail'
    	elif self.outlook is True:
    	    provider = 'outlook'
    	elif self.external_email is True:
    	    provider = 'smtp'
    	else:
    	    provider = 'sendgrid'

    	return provider
