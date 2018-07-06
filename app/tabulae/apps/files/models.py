# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Third-party app imports
import storages.backends.s3boto

# Imports from app
from tabulae.apps.general.models import BaseModel

# Setup private storages for s3boto
# By default it's public
protected_storage = storages.backends.s3boto.S3BotoStorage(
    acl='private',
)

public_storage = storages.backends.s3boto.S3BotoStorage(
    acl='public-read',
)


class File(BaseModel):
    original_name = models.TextField(blank=False, default='')
    file_name = models.TextField(blank=False, default='')

    url = models.URLField(blank=False, default='')

    content_type = models.TextField(blank=False, default='')

    file = models.FileField(
        null=True,
        blank=True,
        storage=protected_storage,
        upload_to='media_lists/%Y/%m/%d',
    )

    header_names = ArrayField(models.CharField(
        max_length=200), blank=True, default=list)
    order = ArrayField(models.CharField(
        max_length=200), blank=True, default=list)

    imported = models.BooleanField(blank=False, default=False)
    file_exists = models.BooleanField(blank=False, default=False)


class EmailImage(BaseModel):
    original_name = models.TextField(blank=False, default='')
    file_name = models.TextField(blank=False, default='')

    file = models.FileField(
        null=True,
        blank=True,
        storage=public_storage,
        upload_to='image/%Y/%m/%d',
    )
