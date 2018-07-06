# -*- coding: utf-8 -*-
# Core Django imports
from tabulae.models import User
from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=True)

    created_by = models.ForeignKey(User, related_name='+', null=True)

    class Meta:
        abstract = True
