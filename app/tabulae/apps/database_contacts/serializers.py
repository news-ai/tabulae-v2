# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework.serializers import (
	ModelSerializer,
	Serializer,
	CharField,
	BooleanField,
	IntegerField,
	ListField,
	URLField,
)

# Imports from app
from tabulae.apps.general.response import form_response
from .models import (
	DatabaseContact,
	Organization,
	ContactInfo,
	SocialProfile,
	Photo,
	WritingInformation,
	DigitalFootprint,
	Score,
	Topic,
	Demographic,
	LocationDeduced,
	City,
	State,
	Country,
	Continent,
)


class OrganizationSerializer(Serializer):
	name = CharField(required=False)
	title = CharField(required=False)

	start_date = CharField(required=False)
	startDate = CharField(source='start_date', required=False)

	end_date = CharField(required=False)
	endDate = CharField(source='end_date', required=False)

	def to_representation(self, obj):
		return {
			'name': obj.name,
			'title': obj.title,
			'startDate': obj.start_date,
			'endDate': obj.end_date,
		}

	class Meta:
		model = Organization
		fields = ('name', 'title', 'start_date', 'end_date',
				  'startDate', 'endDate',)


class ContactInfoSerializer(Serializer):
	given_name = CharField(required=False)
	givenName = CharField(source='given_name', required=False)

	full_name = CharField(required=False)
	fullName = CharField(source='full_name', required=False)

	family_name = CharField(required=False)
	familyName = CharField(source='family_name', required=False)

	websites = ListField(child=CharField(max_length=200,
										 allow_blank=True))

	def to_representation(self, obj):
		return {
			'givenName': obj.given_name,
			'fullName': obj.full_name,
			'familyName': obj.family_name,
			'websites': obj.websites,
		}

	class Meta:
		model = ContactInfo
		fields = ('given_name', 'givenName', 'full_name',
				  'fullName', 'family_name', 'familyName',
				  'websites',)


class SocialProfileSerializer(Serializer):

	username = CharField(required=False)
	bio = CharField(required=False)

	type_id = CharField(required=False)
	typeId = CharField(source='type_id', required=False)

	url = URLField(required=False)

	type_name = CharField(required=False)
	typeName = CharField(source='type_name', required=False)

	network = CharField(required=False)
	type = CharField(source='network', required=False)

	user_id = CharField(required=False)
	id = CharField(source='user_id', required=False)

	def to_representation(self, obj):
		return {
			'username': obj.username,
			'bio': obj.bio,
			'typeId': obj.type_id,
			'url': obj.url,
			'typeName': obj.type_name,
			'type': obj.network,
			'id': obj.user_id,
			# 'followers': 0
			# 'following': 0
		}

	class Meta:
		model = SocialProfile
		fields = ('username', 'bio', 'type_id', 'url',
				  'type_name', 'network', 'user_id', 'id',
				  'type', 'typeName', 'typeId',)


class PhotoSerializer(Serializer):

	photo_type = CharField(required=False)
	type = CharField(source='photo_type', required=False)

	type_id = CharField(required=False)
	typeId = CharField(source='type_id', required=False)

	type_name = CharField(required=False)
	typeName = CharField(source='type_name', required=False)

	is_primary = BooleanField(required=False)
	isPrimary = BooleanField(source='is_primary', required=False)

	url = URLField(required=False)

	def to_representation(self, obj):
		return {
			'type': obj.photo_type,
			'typeId': obj.type_id,
			'typeName': obj.type_name,
			'isPrimary': obj.is_primary,
			'url': obj.url,
		}

	class Meta:
		model = Photo
		fields = ('photo_type', 'type_id', 'type_name',
				  'is_primary', 'url', 'type', 'typeId',
				  'typeName', 'isPrimary',)


class WritingInformationSerializer(Serializer):

	beats = ListField(child=CharField(max_length=200, allow_blank=True))

	occasional_beats = ListField(child=CharField(max_length=200,
												 allow_blank=True),
								 required=False)
	occasionalBeats = ListField(source='occasional_beats',
								child=CharField(max_length=200,
												allow_blank=True),
								required=False)

	is_freelancer = BooleanField(required=False)
	isFreelancer = BooleanField(source='is_freelancer', required=False)

	is_influencer = BooleanField(required=False)
	isInfluencer = BooleanField(source='is_influencer', required=False)

	rss = ListField(child=CharField(
		max_length=200, allow_blank=True), required=False)

	def to_representation(self, obj):
		return {
			'beats': obj.beats,
			'occasionalBeats': obj.occasional_beats,
			'isFreelancer': obj.is_freelancer,
			'isInfluencer': obj.is_influencer,
			'rss': obj.rss and obj.rss.values(),
		}

	class Meta:
		model = WritingInformation
		fields = ('beats', 'occasional_beats', 'is_freelancer',
				  'is_influencer', 'rss', 'isInfluencer',
				  'isFreelancer', 'occasionalBeats',)


class ScoreSerializer(Serializer):

	score_type = CharField(required=False)
	type = CharField(source='score_type', required=False)

	value = CharField(required=False)
	provider = CharField(required=False)

	def to_representation(self, obj):
		return {
			'type': obj.score_type,
			'value': obj.value,
			'provider': obj.provider,
		}

	class Meta:
		model = Score
		fields = ('type', 'value', 'provider', 'score_type',)


class TopicSerializer(Serializer):

	value = CharField(required=False)
	provider = CharField(required=False)

	def to_representation(self, obj):
		return {
			'value': obj.value,
			'provider': obj.provider,
		}

	class Meta:
		model = Topic
		fields = ('value', 'provider',)


class DigitalFootprintSerializer(Serializer):

	topics = TopicSerializer(many=True, required=False)
	scores = ScoreSerializer(many=True, required=False)

	def to_representation(self, obj):
		return {
			'topics': TopicSerializer(obj.topics, many=True).data,
			'scores': ScoreSerializer(obj.scores, many=True).data,
		}

	class Meta:
		model = DigitalFootprint
		fields = ('topics', 'scores',)


class CitySerializer(Serializer):

	name = CharField(required=False)

	def to_representation(self, obj):
		return {
			'name': obj.name,
		}

	class Meta:
		model = City
		fields = ('name',)


class StateSerializer(Serializer):

	code = CharField(required=False)
	name = CharField(required=False)

	def to_representation(self, obj):
		return {
			'code': obj.code,
			'name': obj.name,
		}

	class Meta:
		model = State
		fields = ('code', 'name',)


class CountrySerializer(Serializer):

	code = CharField(required=False)
	name = CharField(required=False)
	deduced = BooleanField(required=False)

	def to_representation(self, obj):
		return {
			'code': obj.code,
			'name': obj.name,
			'deduced': obj.deduced,
		}

	class Meta:
		model = Country
		fields = ('code', 'name', 'deduced',)


class ContinentSerializer(Serializer):

	code = CharField(required=False)
	deduced = BooleanField(required=False)

	def to_representation(self, obj):
		return {
			'name': obj.name,
			'deduced': obj.deduced,
		}

	class Meta:
		model = Continent
		fields = ('name', 'deduced',)


class LocationDeducedSerializer(Serializer):
	city = CitySerializer(required=False)
	state = StateSerializer(required=False)
	country = CountrySerializer(required=False)
	continent = ContinentSerializer(required=False)

	normalized_location = CharField(required=False)
	normalizedLocation = CharField(
		source='normalized_location', required=False)

	deduced_location = CharField(required=False)
	deducedLocation = CharField(source='deduced_location', required=False)

	likelihood = IntegerField(required=False)

	def to_representation(self, obj):
		return {
			'city': CitySerializer(obj.city).data,
			'state': StateSerializer(obj.state).data,
			'country': CountrySerializer(obj.country).data,
			'continent': ContinentSerializer(obj.continent).data,
			'normalizedLocation': obj.normalized_location,
			'deducedLocation': obj.deduced_location,
			'likelihood': obj.likelihood,
		}

	class Meta:
		model = LocationDeduced
		fields = ('city', 'state', 'country', 'continent',
				  'normalized_location', 'deduced_location', 'likelihood',
				  'normalizedLocation', 'deducedLocation',)


class DemographicSerializer(Serializer):
	gender = CharField(required=False)

	location_general = CharField(required=False)
	locationGeneral = CharField(source='location_general', required=False)

	location_deduced = LocationDeducedSerializer(required=False)
	locationDeduced = LocationDeducedSerializer(
		source='location_deduced', required=False)

	def to_representation(self, obj):
		return {
			'gender': obj.gender,
			'locationGeneral': obj.location_general,
			'locationDeduced': (
				LocationDeducedSerializer(obj.location_deduced).data),
		}

	class Meta:
		model = Demographic
		fields = ('gender', 'location_general', 'location_deduced',
				  'locationGeneral', 'locationDeduced',)


class DatabaseContactSerializer(ModelSerializer):
	verified = BooleanField(required=False)

	to_update = BooleanField(required=False)
	toUpdate = BooleanField(source='to_update', required=False)

	is_outdated = BooleanField(required=False)
	isOutdated = BooleanField(source='is_outdated', required=False)

	organizations = OrganizationSerializer(many=True, required=False)

	digital_footprint = DigitalFootprintSerializer(required=False)
	digitalFootprint = DigitalFootprintSerializer(
		source='digital_footprint', required=False)

	social_profiles = SocialProfileSerializer(many=True, required=False)
	socialProfiles = SocialProfileSerializer(
		source='social_profiles', many=True, required=False)

	demographics = DemographicSerializer(required=False)
	photos = PhotoSerializer(required=False, many=True)

	contact_info = ContactInfoSerializer(required=False)
	contactInfo = ContactInfoSerializer(
		source='contact_info', required=False)

	writing_information = WritingInformationSerializer(required=False)
	writingInformation = WritingInformationSerializer(
		source='writing_information', required=False)

	def to_representation(self, obj):
		database_contact = {
			'id': obj.pk,
			'email': obj.email,
			'organizations': (OrganizationSerializer(obj.organizations,
													 many=True).data),
			'digitalFootprint': (
				DigitalFootprintSerializer(obj.digital_footprint).data),
			'socialProfiles': (SocialProfileSerializer(obj.social_profiles,
													   many=True).data),
			'demographics': (DemographicSerializer(obj.demographics).data),
			'photos': (PhotoSerializer(obj.photos, many=True).data),
			'contactInfo': (ContactInfoSerializer(obj.contact_info).data),
			'writingInformation': (
				WritingInformationSerializer(obj.writing_information).data),
			'verified': obj.verified,
			'toUpdate': obj.to_update,
			'isOutdated': obj.is_outdated,
			'fullcontact': obj.full_contact,
			'clearbit': obj.clear_bit,
			'created': obj.created,
			'updated': obj.updated,
		}

		return database_contact

	def create(self, data):
		organizations = []
		digital_footprint = None
		social_profiles = []
		demographics = None
		photos = []
		contact_info = None
		writing_information = None

		request = self.context.get('request')

		if 'organizations' in data:
			organizations = data.pop('organizations')

		if 'digital_footprint' in data:
			digital_footprint = data.pop('digital_footprint')

		if 'social_profiles' in data:
			social_profiles = data.pop('social_profiles')

		if 'demographics' in data:
			demographics = data.pop('demographics')

		if 'photos' in data:
			photos = data.pop('photos')

		if 'contact_info' in data:
			contact_info = data.pop('contact_info')

		if 'writing_information' in data:
			writing_information = data.pop('writing_information')

		contact = DatabaseContact.objects.create(**data)

		if len(organizations) > 0:
			for organization_dict in organizations:
				organization = Organization.objects.create(
					created_by=request.user, **organization_dict)
				contact.organizations.add(organization)

		if digital_footprint:
			digital_footprint_django = DigitalFootprint.objects.create(
				created_by=request.user)

			# Normalize topics
			if 'topics' in digital_footprint:
				for topic in digital_footprint['topics']:
					if ('value' in topic and 'provider' in topic):
						django_topic, created = Topic.objects.get_or_create(
							value=topic['value'],
							provider=topic['provider'])
						digital_footprint_django.topics.add(django_topic)

			# Normaliize scores
			if 'scores' in digital_footprint:
				for score in digital_footprint['scores']:
					if ('type' in score and 'value' in score
							and 'provider' in score):
						django_score = Score.objects.create(
							score_type=score['type'],
							value=score['value'],
							provider=score['provider']
						)
						digital_footprint_django.scores.add(django_score)

			# Add to contact model
			digital_footprint_django.save()
			contact.digital_footprint = digital_footprint_django

		if len(social_profiles) > 0:
			for social_profile_dict in social_profiles:
				social_profile = SocialProfile.objects.create(
					created_by=request.user, **social_profile_dict)
				contact.social_profiles.add(social_profile)

		if demographics:
			city = None
			state = None
			country = None
			continent = None
			location_deduced = None

			if 'location_deduced' in demographics:
				location_deduced = demographics.pop('location_deduced')

			if location_deduced:
				if 'city' in location_deduced:
					city = location_deduced.pop('city')

				if 'state' in location_deduced:
					state = location_deduced.pop('state')

				if 'country' in location_deduced:
					country = location_deduced.pop('country')

				if 'continent' in location_deduced:
					continent = location_deduced.pop('continent')

			location = LocationDeduced.objects.create(
				created_by=request.user, **location_deduced)

			# Normalize city
			if city:
				if 'name' in city:
					django_city, created = City.objects.get_or_create(
						name=city['name'])
					location.city = django_city

			# Normalize state
			if state:
				if 'code' in state:
					state_code = state.get('code', '')
					state_name = state.get('name', '')

					# Add or find state
					django_state, created = State.objects.get_or_create(
						code=state_code, name=state_name)
					location.state = django_state

			# Normalize country
			if country:
				if 'code' in country:
					country_code = country.get('code', '')
					country_name = country.get('name', '')
					country_deduced = country.get('deduced', False)

					# Add or find country
					django_country, created = (
						Country.objects.get_or_create(
							code=country_code, name=country_name))

					# If true (since default is False)
					if country_deduced:
						django_country.deduced = country_deduced
						django_country.save()
					location.country = django_country

			# Normalize continent
			if continent:
				if 'code' in continent:
					continent_code = continent.get('code', '')
					continent_deduced = continent.get('deduced', False)

					# Add or find continent
					django_continent, created = (
						Continent.objects.get_or_create(
							code=continent_code))

					# If true (since default is False)
					if continent_deduced:
						django_continent.deduced = continent_deduced
						django_continent.save()
					location.continent = django_continent

			location.save()
			demographics.location_deduced = location
			demographic = Demographic.objects.create(
				created_by=request.user, **demographics)
			contact.demographics = demographic

		if len(photos) > 0:
			for photo_dict in photos:
				photo = Photo.objects.create(
					created_by=request.user, **photo_dict)
				contact.photos.add(photo)

		if contact_info:
			info = ContactInfo.objects.create(
				created_by=request.user, **contact_info)
			contact.contact_info = info

		if writing_information:
			info = WritingInformation.objects.create(
				created_by=request.user, **writing_information)
			contact.writing_information = info

		contact.created_by = request.user
		contact.save()

		return contact

	class Meta:
		model = DatabaseContact
		fields = ('email',)
		lookup_field = 'email'
		extra_kwargs = {
			'url': {'lookup_field': 'email'}
		}
		fields = ('organizations', 'digitalFootprint', 'socialProfiles',
				  'demographics', 'photos', 'contactInfo',
				  'writingInformation', 'digital_footprint', 'email',
				  'social_profiles', 'contact_info', 'writing_information',
				  'verified', 'to_update', 'is_outdated', 'full_contact',
				  'clear_bit', 'toUpdate', 'isOutdated')
