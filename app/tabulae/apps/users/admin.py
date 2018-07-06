# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib import admin

# Imports from app
from .models import UserProfile, Agency, Team, Client, Invite, Billing, EmailCode

admin.site.register(EmailCode)
admin.site.register(UserProfile)
admin.site.register(Agency)
admin.site.register(Team)
admin.site.register(Client)
admin.site.register(Invite)
admin.site.register(Billing)
