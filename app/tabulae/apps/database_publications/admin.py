# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib import admin

# Imports from app
from .models import DatabasePublication

admin.site.register(DatabasePublication)
