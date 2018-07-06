# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib import admin

# Imports from app
from .models import Contact, CustomContactField

admin.site.register(CustomContactField)
admin.site.register(Contact)