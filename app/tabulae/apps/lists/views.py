# -*- coding: utf-8 -*-
# Stdlib imports
import datetime
import os
import binascii

# Core Django imports
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# Third-party app imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)
from rest_framework.exceptions import NotAuthenticated, ParseError

# Imports from app
from tabulae.apps.general.viewset import NewsAIModelViewSet
from tabulae.apps.general.pagination import GlobalPagination
from tabulae.apps.general.response import Response, BulkResponse
from tabulae.apps.general.elastic_search import es
from tabulae.apps.general.permissions import IsAdminOrIsSelf
from tabulae.apps.files.models import File
from tabulae.apps.files.serializers import FileSerializer
from tabulae.apps.contacts.models import Contact
from tabulae.apps.emails.serializers import EmailSerializer
from tabulae.apps.publications.serializers import PublicationSerializer
from tabulae.apps.emails.models import Email
from tabulae.apps.contacts.serializers import ContactSerializer
from tabulae.apps.users.models import UserProfile
from tabulae.apps.feeds.models import Feed
from .models import MediaList, CustomFieldsMap
from .serializers import MediaListSerializer
from .permissions import MediaListPermission


class MediaListViewSet(NewsAIModelViewSet):
    '''
        left (priority):
        left (not): resync
    '''
    queryset = MediaList.objects.all()
    serializer_class = MediaListSerializer
    pagination_serializer_class = GlobalPagination
    permission_classes = (MediaListPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter,)
    paginate_by_param = 'limit'
    ordering_fields = '__all__'
    filter_fields = ('tags__name', 'client_name',)
    search_fields = ('name',)

    def get_media_list_by_pk(self, request, pk):
        if request.user and request.user.is_authenticated():
            user_profile = UserProfile.objects.get(user=request.user)
            queryset = MediaList.objects.filter(team=user_profile.team)
            media_list = get_object_or_404(queryset, pk=pk)
            return media_list
        raise NotAuthenticated()

    def retrieve(self, request, pk=None):
        if request.user and request.user.is_authenticated():
            media_list = self.get_media_list_by_pk(request, pk)
            serializer = MediaListSerializer(media_list)
            return Response(serializer.data, {})
        raise NotAuthenticated()

    def list(self, request):
        if request.user and request.user.is_authenticated():
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return BulkResponse(serializer.data, {},
                                len(serializer.data), len(serializer.data))
        raise NotAuthenticated()

    def destroy(self, request, pk, format=None):
        if request.user and request.user.is_authenticated():
            media_list = self.get_media_list_by_pk(request, pk)
            media_list.is_deleted = True
            media_list.save()

            serializer = MediaListSerializer(media_list)
            return Response(serializer.data, {})
        raise NotAuthenticated()

    def get_queryset(self,):
        if self.request.user and self.request.user.is_authenticated():
            user_profile = UserProfile.objects.get(user=self.request.user)
            return MediaList.objects.filter(
                created_by=self.request.user,
                archived=False,
                is_deleted=False,
                team=user_profile.team
            ).order_by('-created')
        raise NotAuthenticated()

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']

            if isinstance(data, list):
                kwargs['many'] = True
        return super(MediaListViewSet, self).get_serializer(*args, **kwargs)

    # GET /lists/<id> if id == 'archived' (External)
    @list_route(methods=['get'], url_path='archived',
                permission_classes=[IsAdminOrIsSelf])
    def archived(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        media_lists = MediaList.objects.filter(
            created_by=request.user,
            team=user_profile.team,
            archived=True,
            is_deleted=False
        ).order_by('-created')

        page = self.paginate_queryset(media_lists)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(media_lists, many=True)
        return BulkResponse(serializer.data, {},
                            len(serializer.data), len(serializer.data))

    # GET /lists/<id> if id == 'clients' (External)
    @list_route(methods=['get'], url_path='clients',
                permission_classes=[IsAdminOrIsSelf])
    def clients(self, request):
        # Retrieve all distinct clients
        user_profile = UserProfile.objects.get(user=request.user)
        media_lists = MediaList.objects.filter(
            team=user_profile.team,
            is_deleted=False,
            archived=False
        ).exclude(
            Q(client_name__isnull=True) | Q(client_name='')
        ).values_list('client_name', flat=True).distinct()
        clients = media_lists.values_list('client_name', flat=True)

        # Create a false response structure
        data = {
            'clients': clients
        }
        return BulkResponse(data, {}, len(clients), len(clients))

    # GET /lists/<id> if id == 'public' (External)
    @list_route(methods=['get'], url_path='public',
                permission_classes=[IsAdminOrIsSelf])
    def public(self, request):
        media_lists = MediaList.objects.filter(public_list=True)

        page = self.paginate_queryset(media_lists)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(media_lists, many=True)
        return BulkResponse(serializer.data, {},
                            len(serializer.data), len(serializer.data))

    # GET /lists/<id> if id == 'team' (External)
    @list_route(methods=['get'], url_path='team',
                permission_classes=[IsAdminOrIsSelf])
    def team(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        media_lists = MediaList.objects.none()
        if user_profile.team:
            media_lists = MediaList.objects.filter(
                team=user_profile.team,
                is_deleted=False,
                archived=False
            ).filter(~Q(created_by=self.request.user))

        page = self.paginate_queryset(media_lists)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(media_lists, many=True)
        return BulkResponse(serializer.data, {},
                            len(serializer.data), len(serializer.data))

    # GET /lists/<id>/contacts (External)
    @detail_route(methods=['get'], url_path='contacts',
                  permission_classes=[IsAdminOrIsSelf])
    def contacts(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)
        queryset = media_list.contacts and media_list.contacts.get_queryset()
        queryset = OrderingFilter().filter_queryset(request, queryset, self)

        # We have to create a search filter
        self.search_fields = ('=first_name', '=last_name',
                              '=email', '=employers__name',
                              '=custom_fields__value',)
        queryset = SearchFilter().filter_queryset(request, queryset, self)
        queryset = queryset.order_by('-created')

        page = self.paginate_queryset(queryset)
        if page is not None:
            included = []

            # Initialize included
            publications = []
            for contact in page:
                publication = []
                if contact.employers.count() > 0:
                    publication += list(contact.employers.all())
                if contact.past_employers.count() > 0:
                    publication += list(contact.past_employers.all())
                if len(publication) > 0:
                    publications += publication

            if len(publications) > 0:
                pub_serializer = PublicationSerializer(
                    publications, many=True)
                included = pub_serializer.data

            serializer = ContactSerializer(page, many=True)
            return self.get_paginated_response(serializer.data, included)

        serializer = ContactSerializer(queryset, many=True)
        return BulkResponse(serializer.data, {},
                            len(serializer.data), len(serializer.data))

    # GET /lists/<id>/headlines (External)
    @detail_route(methods=['get'], url_path='headlines',
                  permission_classes=[IsAdminOrIsSelf])
    def headlines(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)
        contacts = media_list.contacts.all()

        # Response to user
        headlines = []
        total_headlines = 0

        should = []
        for contact in contacts:
            feeds = Feed.objects.filter(
                contact=contact, valid_feed=True,
                running=True)
            for feed in feeds:
                if feed.feed_url != '':
                    should.append({
                        'match': {
                            'data.FeedURL': feed.feed_url
                        }
                    })

        if len(should) > 0:
            query = {
                'size': 20,
                'from': 0,
                'query': {
                    'bool': {
                        'should': should
                    }
                },
                'sort': [{
                    'data.PublishDate': {
                        'order': 'desc',
                        'mode': 'avg'
                    }
                }]
            }

            es_headlines = es.search(
                index='headlines', doc_type='headline', body=query)

            if 'hits' in es_headlines and 'total' in es_headlines['hits']:
                total_headlines = es_headlines['hits']['total']

            if 'hits' in es_headlines and 'hits' in es_headlines['hits']:
                for es_headline in es_headlines['hits']['hits']:
                    if ('_source' in es_headline and
                            'data' in es_headline['_source']):
                        headlines.append(es_headline['_source']['data'])
        return BulkResponse(headlines, {}, len(headlines),
                            total_headlines)

    # GET /lists/<id>/tweets (Internal)
    @detail_route(methods=['get'], url_path='tweets',
                  permission_classes=[IsAdminOrIsSelf])
    def tweets(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)

        total_tweets = 0
        tweets = []

        if media_list.contacts.count() > 0:
            twitter_usernames = (media_list.contacts and
                                 media_list.contacts.values_list(
                                     'twitter', flat=True))
            if len(twitter_usernames) > 0:
                query = {
                    'size': 20,
                    'from': 0,
                    'query': {
                        'bool': {
                            'should': [],
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

                for username in twitter_usernames:
                    query['query']['bool']['should'].append({
                        'term': {
                            'data.Username': username
                        }
                    })

                es_tweets = es.search(
                    index='tweets', doc_type='tweet', body=query)

                if 'hits' in es_tweets and 'total' in es_tweets['hits']:
                    total_tweets = es_tweets['hits']['total']

                if 'hits' in es_tweets and 'hits' in es_tweets['hits']:
                    for es_tweet in es_tweets['hits']['hits']:
                        if ('_source' in es_tweet and
                                'data' in es_tweet['_source']):
                            tweets.append(es_tweet['_source']['data'])
        return BulkResponse(tweets, {}, len(tweets), total_tweets)

    # GET /lists/<id>/feed (External)
    @detail_route(methods=['get'], url_path='feed',
                  permission_classes=[IsAdminOrIsSelf])
    def feed(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)

        # Response to user
        feed = []
        total_feed = 0

        # ES attributes
        should = []

        if media_list.contacts.count() > 0:
            twitter_usernames = (media_list.contacts and
                                 media_list.contacts.values_list(
                                     'twitter', flat=True))
            instagram_usernames = (media_list.contacts and
                                   media_list.contacts.values_list(
                                       'instagram', flat=True))

            feed_urls = []
            contacts = media_list.contacts.all()
            for contact in contacts:
                feeds = Feed.objects.filter(
                    contact=contact, valid_feed=True,
                    running=True)
                for feed in feeds:
                    if feed.feed_url != '':
                        feed_urls.append(feed.feed_url)

            for twitter in twitter_usernames:
                if twitter != '':
                    should.append({
                        'term': {
                            'data.Username': twitter
                        }
                    })

            for instagram in instagram_usernames:
                if instagram != '':
                    should.append({
                        'term': {
                            'data.InstagramUsername': instagram
                        }
                    })

            for feed_url in feed_urls:
                if feed_url != '':
                    should.append({
                        'term': {
                            'data.FeedURL': feed_url
                        }
                    })

        if len(should) > 0:
            query = {
                'size': 20,
                'from': 0,
                'query': {
                    'bool': {
                        'should': should
                    }
                },
                'sort': [{
                    'data.CreatedAt': {
                        'order': 'desc',
                        'mode': 'avg'
                    }
                }]
            }

            es_feeds = es.search(
                index='feeds', doc_type='feed', body=query)

            if 'hits' in es_feeds and 'total' in es_feeds['hits']:
                total_feed = es_feeds['hits']['total']

            if 'hits' in es_feeds and 'hits' in es_feeds['hits']:
                for es_feed in es_feeds['hits']['hits']:
                    if ('_source' in es_feed and
                            'data' in es_feed['_source']):
                        feed.append(es_feed['_source']['data'])
        return BulkResponse(feed, {}, len(feed), total_feed)

    # GET /lists/<id>/emails (External)
    @detail_route(methods=['get'], url_path='emails',
                  permission_classes=[IsAdminOrIsSelf])
    def emails(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)
        queryset = Email.objects.filter(
            created_by=request.user, list_in=media_list).order_by('-created')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EmailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EmailSerializer(queryset, many=True)
        return BulkResponse(serializer.data, {},
                            len(serializer.data), len(serializer.data))

    # GET /lists/<id>/public (External)
    @detail_route(methods=['get'], url_path='public',
                  permission_classes=[IsAdminOrIsSelf])
    def public(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)
        media_list.public_list = True
        media_list.save()
        serializer = MediaListSerializer(media_list)
        return Response(serializer.data, {})

    # GET /lists/<id>/archive (External)
    @detail_route(methods=['get'], url_path='archive',
                  permission_classes=[IsAdminOrIsSelf])
    def archive(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)
        media_list.archived = not media_list.archived
        media_list.save()
        serializer = MediaListSerializer(media_list)
        return Response(serializer.data, {})

    # POST /lists/<id>/upload (External)
    @detail_route(methods=['post'], url_path='upload',
                  permission_classes=[IsAdminOrIsSelf],
                  parser_classes=(FormParser, MultiPartParser,))
    def upload(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)
        if 'file' in request.FILES:
            xlsx_file = request.FILES.get('file')
            random_number = binascii.b2a_hex(os.urandom(15))

            original_file_name = xlsx_file._name
            file_name = xlsx_file._name.replace(' ', '')
            generated_file_name = ''.join(
                [str(request.user.pk), random_number, file_name])
            xlsx_file._name = generated_file_name

            file = File(file=xlsx_file)
            file.original_name = original_file_name
            file.file_exists = True
            file.file_name = generated_file_name
            file.created_by = request.user
            file.save()

            media_list.file = file
            media_list.save()

            serializer = FileSerializer(file)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /lists/<id>/add-custom-field (External)
    @detail_route(methods=['post'], url_path='add-custom-field',
                  permission_classes=[IsAdminOrIsSelf])
    def add_custom_field(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)

        if ('name' in request.data and 'value' in request.data and
                'customfield' in request.data and 'hidden' in request.data):
            field_map = CustomFieldsMap(name=request.data['name'],
                                        value=request.data['value'],
                                        custom_field=request.data[
                                            'customfield'],
                                        hidden=request.data['hidden'])
            field_map.save()
            media_list.fields_map.add(field_map)

            serializer = MediaListSerializer(media_list)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /lists/<id>/add-tags (External)
    @detail_route(methods=['post'], url_path='add-tags',
                  permission_classes=[IsAdminOrIsSelf])
    def add_tags(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)
        if 'tags' in request.data:
            for tag in request.data['tags']:
                media_list.tags.add(tag)
                media_list.save()
                serializer = MediaListSerializer(media_list)
                return Response(serializer.data, {})
        raise ParseError()

    # POST /lists/<id>/remove-tags (External)
    @detail_route(methods=['post'], url_path='remove-tags',
                  permission_classes=[IsAdminOrIsSelf])
    def remove_tags(self, request, pk=None):
        media_list = self.get_media_list_by_pk(request, pk)
        if 'tags' in request.data:
            for tag in request.data['tags']:
                media_list.tags.remove(tag)
                media_list.save()
                serializer = MediaListSerializer(media_list)
                return Response(serializer.data, {})
        raise ParseError()

    # POST /lists/<id>/twittertimeseries (External)
    @detail_route(methods=['post'], url_path='twittertimeseries',
                  permission_classes=[IsAdminOrIsSelf])
    def twitter_timeseries(self, request, pk=None):
        if 'ids' in request.data and 'days' in request.data:
            timeseries = []

            twitter_usernames = []

            for contact_id in request.data['ids']:
                contact = Contact.objects.get(pk=contact_id)
                if contact.twitter != '':
                    twitter_usernames.append(contact.twitter)

            if len(twitter_usernames) > 0:
                # Set how many dates we want to look behind
                default_date = 7
                if request.data['days'] != 0:
                    default_date = request.data['days']

                # Add all twitter ids to ES ids
                elastic_ids = []
                for twitter in twitter_usernames:
                    if twitter != '':
                        for i in xrange(0, default_date):
                            consider_date = (
                                datetime.date.today() -
                                datetime.timedelta(days=i))
                            single_date = consider_date.strftime('%Y-%m-%d')
                            elastic_ids.append(twitter + '-' + single_date)

                if len(elastic_ids) > 0:
                    query = {
                        'ids': elastic_ids
                    }

                    es_timeseries = es.mget(
                        index='timeseries', doc_type='twitter', body=query)

                    if 'docs' in es_timeseries:
                        for ts in es_timeseries['docs']:
                            if ts['found']:
                                if '_source' in ts and 'data' in ts['_source']:
                                    timeseries.append(ts['_source']['data'])
            return BulkResponse(timeseries, {}, len(timeseries),
                                len(timeseries))
        raise ParseError()

    # POST /lists/<id>/instagramtimeseries (External)
    @detail_route(methods=['post'], url_path='instagramtimeseries',
                  permission_classes=[IsAdminOrIsSelf])
    def instagram_timeseries(self, request, pk=None):
        if 'ids' in request.data and 'days' in request.data:
            timeseries = []

            instagram_usernames = []

            for contact_id in request.data['ids']:
                contact = Contact.objects.get(pk=contact_id)
                if contact.instagram != '':
                    instagram_usernames.append(contact.instagram)

            if len(instagram_usernames) > 0:
                # Set how many dates we want to look behind
                default_date = 7
                if request.data['days'] != 0:
                    default_date = request.data['days']

                # Add all instagram ids to ES ids
                elastic_ids = []
                for instagram in instagram_usernames:
                    if instagram != '':
                        for i in xrange(0, default_date):
                            consider_date = (
                                datetime.date.today() -
                                datetime.timedelta(days=i))
                            single_date = consider_date.strftime('%Y-%m-%d')
                            elastic_ids.append(instagram + '-' + single_date)

                if len(elastic_ids) > 0:
                    query = {
                        'ids': elastic_ids
                    }

                    es_timeseries = es.mget(
                        index='timeseries', doc_type='instagram', body=query)

                    if 'docs' in es_timeseries:
                        for ts in es_timeseries['docs']:
                            if ts['found']:
                                if '_source' in ts and 'data' in ts['_source']:
                                    timeseries.append(ts['_source']['data'])

            return BulkResponse(timeseries, {}, len(timeseries),
                                len(timeseries))
        raise ParseError()

    # POST /lists/<id>/duplicate (External)
    @detail_route(methods=['post'], url_path='duplicate',
                  permission_classes=[IsAdminOrIsSelf])
    def duplicate(self, request, pk=None):
        user_profile = UserProfile.objects.get(user=request.user)
        media_list = self.get_media_list_by_pk(request, pk)
        if 'name' in request.data:
            clients = media_list.clients
            contacts = media_list.contacts and media_list.contacts.all()
            fields_map = (
                media_list.fields_map and media_list.fields_map.all())
            tags = media_list.tags and media_list.tags.all()
            file = media_list.file
            team = media_list.team

            media_list.name = request.data['name']
            media_list.pk = None
            media_list.created = datetime.datetime.now()
            media_list.updated = datetime.datetime.now()
            media_list.created_by = request.user
            media_list.team = user_profile.team
            media_list.save()

            if clients.count() > 0:
                media_list.clients.add(*clients)

            if contacts.count() > 0:
                media_list.contacts.add(*contacts)

            if fields_map.count() > 0:
                for field_map in fields_map:
                    # Create field map with a new id
                    field_map.pk = None
                    field_map.created = datetime.datetime.now()
                    field_map.updated = datetime.datetime.now()
                    field_map.save()

                    # Add that field map to the media list
                    media_list.fields_map.add(field_map)

            if tags:
                # Add tags from previous list to new list
                for tag in tags:
                    media_list.tags.add(tag)

            if file:
                media_list.file = file

            if team:
                media_list.team = team

            media_list.save()
            serializer = MediaListSerializer(media_list)
            return Response(serializer.data, {})
        raise ParseError()
