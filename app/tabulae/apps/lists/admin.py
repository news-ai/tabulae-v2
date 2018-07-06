# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib import admin

# Imports from app
from .models import MediaList, CustomFieldsMap

admin.site.register(CustomFieldsMap)
admin.site.register(MediaList)
