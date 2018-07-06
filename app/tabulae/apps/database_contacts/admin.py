# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib import admin

# Imports from app
from .models import (
	DatabaseContact,
	ContactInfo,
	SocialProfile,
	WritingInformation,
	Organization,
	Photo,
	Demographic,
	LocationDeduced,
	Continent,
	Country,
	State,
	City,
	DigitalFootprint,
	Topic,
	Score,
)


admin.site.register(Score)
admin.site.register(Topic)
admin.site.register(DigitalFootprint)
admin.site.register(City)
admin.site.register(State)
admin.site.register(Country)
admin.site.register(Continent)
admin.site.register(LocationDeduced)
admin.site.register(Demographic)
admin.site.register(Photo)
admin.site.register(Organization)
admin.site.register(WritingInformation)
admin.site.register(SocialProfile)
admin.site.register(ContactInfo)
admin.site.register(DatabaseContact)
