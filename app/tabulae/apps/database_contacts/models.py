# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Imports from app
from tabulae.apps.general.models import BaseModel


class Score(BaseModel):
	score_type = models.TextField(blank=True, default='')
	value = models.TextField(blank=True, default='')
	provider = models.TextField(blank=True, default='')

	class Meta:
		verbose_name_plural = 'scores'


class Topic(BaseModel):
	value = models.TextField(blank=True, default='')
	provider = models.TextField(blank=True, default='')

	class Meta:
		unique_together = ('value', 'provider',)
		verbose_name_plural = 'topics'


class DigitalFootprint(BaseModel):
	topics = models.ManyToManyField(
		Topic, blank=True, related_name='+')
	scores = models.ManyToManyField(
		Score, blank=True, related_name='+')

	class Meta:
		verbose_name_plural = 'digital-footprints'


class City(BaseModel):
	name = models.TextField(blank=True, default='', unique=True)

	class Meta:
		verbose_name_plural = 'cities'


class State(BaseModel):
	code = models.TextField(blank=True, default='', unique=True)
	name = models.TextField(blank=True, default='')

	class Meta:
		verbose_name_plural = 'states'


class Country(BaseModel):
	code = models.TextField(blank=True, default='', unique=True)
	name = models.TextField(blank=True, default='')
	deduced = models.BooleanField(blank=True, default=False)

	class Meta:
		verbose_name_plural = 'countries'


class Continent(BaseModel):
	name = models.TextField(blank=True, default='', unique=True)
	deduced = models.BooleanField(blank=True, default=False)

	class Meta:
		verbose_name_plural = 'continents'


class LocationDeduced(BaseModel):
	city = models.ForeignKey(City, related_name='+', null=True)
	state = models.ForeignKey(State, related_name='+', null=True)
	country = models.ForeignKey(Country, related_name='+', null=True)
	continent = models.ForeignKey(Continent, related_name='+', null=True)
	likelihood = models.IntegerField(blank=True, default=0)
	normalized_location = models.TextField(blank=True, default='')
	deduced_location = models.TextField(blank=True, default='')

	class Meta:
		verbose_name_plural = 'location-deduceds'


class Demographic(BaseModel):
	location_deduced = models.OneToOneField(
		LocationDeduced,
		on_delete=models.CASCADE,
		primary_key=True,
	)

	gender = models.TextField(blank=True, default='')
	location_general = models.TextField(blank=True, default='')

	class Meta:
		verbose_name_plural = 'demographics'


class Photo(BaseModel):
	url = models.URLField(blank=True, default='')
	type_id = models.TextField(blank=True, default='')
	is_primary = models.BooleanField(blank=True, default=False)
	photo_type = models.TextField(blank=True, default='')
	type_name = models.TextField(blank=True, default='')

	class Meta:
		verbose_name_plural = 'photos'


class Organization(BaseModel):
	name = models.TextField(blank=True, default='')
	title = models.TextField(blank=True, default='')
	start_date = models.TextField(blank=True, default='')
	end_date = models.TextField(blank=True, default='')

	class Meta:
		verbose_name_plural = 'organizations'


class WritingInformation(BaseModel):
	beats = ArrayField(models.CharField(
		max_length=200), blank=True, null=True, default=list)
	occasional_beats = ArrayField(models.CharField(
		max_length=200), blank=True, default=list)
	is_freelancer = models.BooleanField(blank=True, default=False)
	is_influencer = models.BooleanField(blank=True, default=False)
	rss = ArrayField(models.CharField(
		max_length=200), blank=True, null=True, default=list)

	class Meta:
		verbose_name_plural = 'writing-informations'


class SocialProfile(BaseModel):
	username = models.TextField(blank=True, default='')
	bio = models.TextField(blank=True, default='')
	type_id = models.TextField(blank=True, default='')
	url = models.URLField(blank=True, default='')
	type_name = models.TextField(blank=True, default='')
	network = models.TextField(blank=True, default='')  # type
	followers = models.IntegerField(blank=True, default=0)
	user_id = models.TextField(blank=True, default='')
	following = models.IntegerField(blank=True, default=0)

	class Meta:
		verbose_name_plural = 'social-profiles'


class ContactInfo(BaseModel):
	given_name = models.TextField(blank=True, default='')
	full_name = models.TextField(blank=True, default='')
	family_name = models.TextField(blank=True, default='')
	websites = ArrayField(models.CharField(
		max_length=200), blank=True, default=list)

	class Meta:
		verbose_name_plural = 'contact-infos'


class DatabaseContact(BaseModel):
	email = models.EmailField(blank=False, max_length=254, unique=True)

	organizations = models.ManyToManyField(
		Organization,
		blank=True,
		related_name='+'
	)
	digital_footprint = models.OneToOneField(
		DigitalFootprint,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
	)
	social_profiles = models.ManyToManyField(
		SocialProfile,
		blank=True,
		related_name='+',
	)
	demographics = models.OneToOneField(
		Demographic,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
	)
	photos = models.ManyToManyField(
		Photo,
		blank=True,
		related_name='+'
	)
	contact_info = models.OneToOneField(
		ContactInfo,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
	)
	writing_information = models.OneToOneField(
		WritingInformation,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
	)

	verified = models.BooleanField(blank=True, default=False)
	to_update = models.BooleanField(blank=True, default=False)
	is_outdated = models.BooleanField(blank=True, default=False)

	full_contact = models.BooleanField(blank=True, default=False)
	clear_bit = models.BooleanField(blank=True, default=False)

	class Meta:
		verbose_name_plural = 'database-contacts'
