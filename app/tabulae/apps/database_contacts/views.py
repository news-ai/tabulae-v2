# -*- coding: utf-8 -*-
# Core Django imports
from django.shortcuts import get_object_or_404
from django.http import Http404

# Third-party app imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import OrderingFilter

# Imports from app
from tabulae.apps.general.viewset import NewsAIModelViewSet
from tabulae.apps.general.response import Response, BulkResponse
from tabulae.apps.general.permissions import IsAdminOrIsSelf
from .models import DatabaseContact
from .permissions import DatabaseContactPermission
from .serializers import DatabaseContactSerializer


class DatabaseContactViewSet(NewsAIModelViewSet):
	'''
		left (priority): locations, mapping, search,
		headlines, twitter_profile, twitter_timeseries
		left (not):
	'''
	queryset = DatabaseContact.objects.all()
	serializer_class = DatabaseContactSerializer
	permission_classes = (DatabaseContactPermission,)
	filter_backends = (DjangoFilterBackend, OrderingFilter,)
	paginate_by_param = 'limit'
	ordering_fields = '__all__'
	lookup_value_regex = '[\w\.-]+@[\w\.-]+'
	lookup_field = 'email'

	def get_database_contact_by_pk(self, request, email):
		queryset = DatabaseContact.objects.all()
		try:
			return queryset.get(email=email)
		except queryset.model.DoesNotExist:
			raise Http404('No %s matches the given query.' %
						  queryset.model._meta.object_name)
		return database_contact

	def retrieve(self, request, pk=None, email=None):
		if request.user and request.user.is_authenticated():
			database_contact = self.get_database_contact_by_pk(request, email)
			serializer = DatabaseContactSerializer(database_contact)
			return Response(serializer.data, {})
		raise NotAuthenticated()

	def list(self, request):
		queryset = self.filter_queryset(self.get_queryset())

		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return BulkResponse(serializer.data, {},
							len(serializer.data), len(serializer.data))

	def get_queryset(self,):
		if self.request.user and self.request.user.is_authenticated():
			return DatabaseContact.objects.all().order_by('-created')
		raise NotAuthenticated()

	def get_serializer(self, *args, **kwargs):
		if 'data' in kwargs:
			data = kwargs['data']

			if isinstance(data, list):
				kwargs['many'] = True

		return (super(DatabaseContactViewSet,
					  self).get_serializer(*args, **kwargs))

	# GET /database-contacts/<id> if id == 'locations' (External)
	@list_route(methods=['get'], url_path='locations',
				permission_classes=[IsAdminOrIsSelf])
	def locations(self, request):
		return

	# GET /database-contacts/<id> if id == '_mapping' (External)
	@list_route(methods=['get'], url_path='_mapping',
				permission_classes=[IsAdminOrIsSelf])
	def mapping(self, request):
		return

	# POST /database-contacts/<id> if id == 'search' (External)
	@list_route(methods=['post'], url_path='search',
				permission_classes=[IsAdminOrIsSelf])
	def search(self, request):
		return

	# GET /database-contacts/<email>/tweets (External)
	@detail_route(methods=['get'], url_path='tweets',
				  permission_classes=[IsAdminOrIsSelf])
	def tweets(self, request, email=None):
		database_contact = self.get_database_contact_by_pk(request, email)
		twitter_username = ''

		tweets = []
		total_tweets = 0

		# Get Twitter username
		if database_contact.social_profiles.count() > 0:
			social_profiles = database_contact.social_profiles.all()
			for social_profile in social_profiles:
				if social_profile.network == 'twitter':
					twitter_username = username

		# Search twitter username on Elasticsearch
		if twitter_username != '':
			query = {
				'size': 20,
				'from': 0,
				'query': {
					'bool': {
						'should': [{
							'term': {
								'data.Username': twitter_username
							}
						}],
						'minimum_should_match': '100%'
					}
				},
				'sort': [{
					'data.CreatedAt': {
						'order': 'desc',
						'mode': 'avg'
					}
				}],
			}

			es_tweets = es.search(
				index='tweets', doc_type='md-tweet', body=query)

			if 'hits' in es_tweets and 'total' in es_tweets['hits']:
				total_tweets = es_tweets['hits']['total']

			if 'hits' in es_tweets and 'hits' in es_tweets['hits']:
				for es_tweet in es_tweets['hits']['hits']:
					if ('_source' in es_tweet and
							'data' in es_tweet['_source']):
						tweets.append(es_tweet['_source']['data'])

		return BulkResponse(tweets, {}, len(tweets), total_tweets)

	# GET /database-contacts/<email>/headlines (External)
	@detail_route(methods=['get'], url_path='headlines',
				  permission_classes=[IsAdminOrIsSelf])
	def headlines(self, request, email=None):
		return

	# GET /database-contacts/<email>/twitterprofile (External)
	@detail_route(methods=['get'], url_path='twitterprofile',
				  permission_classes=[IsAdminOrIsSelf])
	def twitter_profile(self, request, email=None):
		return

	# GET /database-contacts/<email>/twittertimeseries (External)
	@detail_route(methods=['get'], url_path='twittertimeseries',
				  permission_classes=[IsAdminOrIsSelf])
	def twitter_timeseries(self, request, email=None):
		return
