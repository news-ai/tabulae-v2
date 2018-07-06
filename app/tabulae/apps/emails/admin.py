# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib import admin

# Imports from app
from .models import Email, Campaign

admin.site.register(Campaign)
admin.site.register(Email)
