# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# Third-party app imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.exceptions import NotAuthenticated, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_201_CREATED
from rest_framework.response import Response as RFREsponse

# Imports from app
from tabulae.apps.general.viewset import NewsAIModelViewSet
from tabulae.apps.general.pagination import GlobalPagination, get_pagination
from tabulae.apps.general.response import Response, BulkResponse
from tabulae.apps.general.elastic_search import es, format_es_response
from tabulae.apps.general.permissions import IsAdminOrIsSelf
from tabulae.apps.emails.models import Email
from tabulae.apps.emails.serializers import EmailSerializer
from tabulae.apps.feeds.serializers import FeedSerializer
from tabulae.apps.publications.models import Publication
from tabulae.apps.publications.serializers import PublicationSerializer
from tabulae.apps.lists.models import MediaList
from tabulae.apps.lists.serializers import MediaListSerializer
from tabulae.apps.feeds.models import Feed
from tabulae.apps.users.models import UserProfile
from .models import Contact
from .serializers import ContactSerializer
from .permissions import ContactPermission


class ContactViewSet(NewsAIModelViewSet):
    '''
        left (priority):
        left (not): enrich
    '''
    serializer_class = ContactSerializer
    permission_classes = (ContactPermission,)
    pagination_serializer_class = GlobalPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter,)
    paginate_by_param = 'limit'
    ordering_fields = '__all__'
    filter_fields = ('email',)
    search_fields = ('first_name', 'last_name', 'email',)

    def get_contact_by_pk(self, request, pk):
        # Switch to team__pk=request.user.team.pk
        user_profile = UserProfile.objects.get(user=request.user)
        queryset = Contact.objects.filter(team=user_profile.team)
        contact = get_object_or_404(queryset, pk=pk)
        return contact

    def get_contact_included(self, contact):
        included = []

        publications = []
        if contact.employers.count() > 0:
            publications += list(contact.employers.all())
        if contact.past_employers.count() > 0:
            publications += list(contact.past_employers.all())

        if len(publications) > 0:
            pub_serializer = PublicationSerializer(
                publications, many=True)
            included = pub_serializer.data

        return included

    def retrieve(self, request, pk=None):
        if request.user and request.user.is_authenticated():
            contact = self.get_contact_by_pk(request, pk)
            included = self.get_contact_included(contact)
            print included

            serializer = ContactSerializer(contact)
            return Response(serializer.data, included)
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
            user_profile = UserProfile.objects.get(user=self.request.user)
            return (
                Contact.objects.filter(
                    team=user_profile.team).order_by(
                    '-created')).prefetch_related(
                'custom_fields')
        raise NotAuthenticated()

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']

            if isinstance(data, list):
                kwargs['many'] = True

        return super(ContactViewSet, self).get_serializer(*args, **kwargs)

    def bulk_update(self, request, pk=None, partial=None, *args, **kwargs):
        '''
            parameters: array of contact objects
        '''
        serializers = []
        included = []
        for contact in request.data:
            if 'id' in contact:
                partial = kwargs.pop('partial', False)
                instance = self.get_contact_by_pk(request, contact['id'])
                serializer = self.get_serializer(
                    instance, data=contact, partial=partial)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                if getattr(instance, '_prefetched_objects_cache', None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

                serializers.append(serializer.data['data'])

        return BulkResponse(serializers, included, len(serializers),
                            len(serializers))

    def update(self, request, pk=None, partial=None, *args, **kwargs):
        '''
            parameters: contact object
        '''
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data['data'], {})

    # POST /lists/<id> if id == 'move' (External)
    @list_route(methods=['post'], url_path='move',
                permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def move(self, request):
        '''
            parameters: contacts: Array, fromList: Int,
            toList: Int
        '''
        contacts = []
        included = []
        if ('contacts' in request.data and 'fromList' in request.data
                and 'toList' in request.data):

            try:
                from_list = MediaList.objects.get(pk=request.data['fromList'])
                to_list = MediaList.objects.get(pk=request.data['toList'])

                for contact_id in request.data['contacts']:
                    try:
                        contact = Contact.objects.get(pk=contact_id)
                        from_list.contacts.remove(contact)
                        to_list.contacts.add(contact)

                        # Add contacts to the list we're going to
                        # return back to user.
                        contacts.append(contact)
                    except Contact.DoesNotExist:
                        continue

                from_list.save()
                from_list_serializer = MediaListSerializer(from_list)
                included.append(from_list_serializer.data)

                to_list.save()
                to_list_serializer = MediaListSerializer(to_list)
                included.append(to_list_serializer.data)

            except MediaList.DoesNotExist:
                pass

        serializer = ContactSerializer(contacts, many=True)
        return BulkResponse(serializer.data, included, len(serializer.data),
                            len(serializer.data))

    # POST /lists/<id> if id == 'copy' (External)
    @list_route(methods=['post'], url_path='copy',
                permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def copy(self, request):
        '''
            parameters: contacts: Array, listid: Int
        '''
        contacts = []
        included = []
        if ('contacts' in request.data and
                'listid' in request.data):
            try:
                media_list = MediaList.objects.get(pk=request.data['listid'])

                for contact_id in request.data['contacts']:
                    try:
                        # Add moved contact to media list
                        contact = Contact.objects.get(pk=contact_id)
                        media_list.contacts.add(contact)

                        # Add contacts to the list we're going to
                        # return back to user.
                        contacts.append(contact)
                    except Contact.DoesNotExist:
                        continue

                media_list.save()
                media_list_serializer = MediaListSerializer(media_list)
                included.append(media_list_serializer.data)
            except MediaList.DoesNotExist:
                pass

        serializer = ContactSerializer(contacts, many=True)
        return BulkResponse(serializer.data, included, len(serializer.data),
                            len(serializer.data))

    # POST /lists/<id> if id == 'bulkdelete' (External)
    @list_route(methods=['post'], url_path='bulkdelete',
                permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def bulk_delete(self, request):
        '''
            parameters: contacts: Array, listid: Int
        '''
        contacts = []
        included = []
        if ('contacts' in request.data and
                'listid' in request.data):
            media_list = MediaList.objects.get(pk=request.data['listid'])
            for contact_id in request.data['contacts']:
                # Remove moved contact from media list
                try:
                    contact = Contact.objects.get(pk=contact_id)

                    # Remove current contact from media_list
                    media_list.contacts.remove(contact)

                    # Add contacts to the list we're going to
                    # return back to user.
                    contacts.append(contact)
                except Contact.DoesNotExist:
                    continue

            media_list.save()
            media_list_serializer = MediaListSerializer(media_list)
            included.append(media_list_serializer.data)

        serializer = ContactSerializer(contacts, many=True)
        return BulkResponse(serializer.data, included, len(serializer.data),
                            len(serializer.data))

    # GET /contacts/<id>/feed (External)
    @detail_route(methods=['get'], url_path='feed',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def feed(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)

        # Response to user
        feed = []
        total_feed = 0

        # ES attributes
        should = []

        twitter_username = contact.twitter
        instagram_username = contact.instagram
        feeds = Feed.objects.filter(
            contact=contact, valid_feed=True,
            running=True)

        if twitter_username != '':
            should.append({
                'term': {
                    'data.Username': twitter_username
                }
            })

        if instagram_username != '':
            should.append({
                'term': {
                    'data.InstagramUsername': instagram_username
                }
            })

        if len(feeds) > 0:
            for feed in feeds:
                should.append({
                    'match': {
                        'data.FeedURL': feed.feed_url
                    }
                })

        if len(should) > 0:
            limit, offset = get_pagination(request)
            query = {
                'size': limit,
                'from': offset,
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
                        es_feed = format_es_response(es_feed)

                        # we want the format to be 'tweets', 'instagrams',
                        # and 'headlines'
                        es_feed['_source']['data']['type'] = es_feed[
                            '_source']['data']['type'].lower() + 's'

                        feed.append(es_feed['_source']['data'])

        return BulkResponse(feed, {}, len(feed),
                            total_feed)

    # GET /contacts/<id>/headlines (External)
    @detail_route(methods=['get'], url_path='headlines',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def headlines(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)

        feeds = Feed.objects.filter(
            contact=contact)

        # Response to user
        headlines = []
        total_headlines = 0

        if len(feeds) > 0:
            limit, offset = get_pagination(request)
            query = {
                'size': limit,
                'from': offset,
                'query': {
                    'bool': {
                        'should': []
                    }
                },
                'sort': [{
                    'data.PublishDate': {
                        'order': 'desc',
                        'mode': 'avg'
                    }
                }]
            }

            for feed in feeds:
                if feed.feed_url != '':
                    query['query']['bool']['should'].append({
                        'match': {
                            'data.FeedURL': feed.feed_url
                        }
                    })

            es_headlines = es.search(
                index='headlines', doc_type='headline', body=query)

            if 'hits' in es_headlines and 'total' in es_headlines['hits']:
                total_headlines = es_headlines['hits']['total']

            if 'hits' in es_headlines and 'hits' in es_headlines['hits']:
                for es_headline in es_headlines['hits']['hits']:
                    if ('_source' in es_headline and
                            'data' in es_headline['_source']):
                        es_headline = format_es_response(es_headline)
                        headlines.append(es_headline['_source']['data'])

        return BulkResponse(headlines, {}, len(headlines),
                            total_headlines)

    # GET /contacts/<id>/tweets (External)
    @detail_route(methods=['get'], url_path='tweets',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def tweets(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)

        # Response to user
        tweets = []
        total_tweets = 0

        if contact.twitter != '':
            limit, offset = get_pagination(request)
            query = {
                'size': limit,
                'from': offset,
                'query': {
                    'bool': {
                        'should': [{
                            'term': {
                                'data.Username': contact.twitter
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
                index='tweets', doc_type='tweet', body=query)

            if 'hits' in es_tweets and 'total' in es_tweets['hits']:
                total_tweets = es_tweets['hits']['total']

            if 'hits' in es_tweets and 'hits' in es_tweets['hits']:
                for es_tweet in es_tweets['hits']['hits']:
                    if ('_source' in es_tweet and
                            'data' in es_tweet['_source']):
                        es_tweet = format_es_response(es_tweet)
                        es_tweet['type'] = 'tweets'
                        tweets.append(es_tweet['_source']['data'])

        return BulkResponse(tweets, {}, len(tweets),
                            total_tweets)

    # GET /contacts/<id>/twitterprofile (External)
    @detail_route(methods=['get'], url_path='twitterprofile',
                  permission_classes=[IsAdminOrIsSelf])
    def twitter_profile(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)

        # Response to user
        twitter_profile = {}

        if contact.twitter != '':
            query = {
                'query': {
                    'bool': {
                        'must': [{
                            'term': {
                                'data.Username': contact.twitter
                            }
                        }]
                    }
                }
            }

            es_twitter_profile = es.search(
                index='tweets', doc_type='user', body=query)
            if ('hits' in es_twitter_profile and
                    'hits' in es_twitter_profile['hits']):
                if len(es_twitter_profile['hits']['hits']) > 0:
                    twitter_profile = es_twitter_profile[
                        'hits']['hits'][0]['_source']['data']

        return Response(twitter_profile, {})

    # GET /contacts/<id>/twittertimeseries (External)
    @detail_route(methods=['get'], url_path='twittertimeseries',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def twitter_timeseries(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)

        # Response to user
        twitter_timeseries = []
        total_twitter_timeseries = 0

        if contact.twitter != '':
            query = {
                'query': {
                    'bool': {
                        'must': [{
                            'term': {
                                'data.Username': contact.twitter
                            }
                        }]
                    }
                },
                'sort': [{
                    'data.CreatedAt': {
                        'order': 'desc',
                        'mode': 'avg'
                    }
                }]
            }

            es_twitter_timeseries = es.search(
                index='timeseries', doc_type='twitter', body=query)

            if ('hits' in es_twitter_timeseries and
                    'total' in es_twitter_timeseries['hits']):
                total_twitter_timeseries = es_twitter_timeseries[
                    'hits']['total']

            if ('hits' in es_twitter_timeseries and
                    'hits' in es_twitter_timeseries['hits']):
                for ts in es_twitter_timeseries['hits']['hits']:
                    if ('_source' in ts and 'data' in ts['_source']):
                        twitter_timeseries.append(ts['_source']['data'])

        return BulkResponse(twitter_timeseries, {}, len(twitter_timeseries),
                            total_twitter_timeseries)

    # GET /contacts/<id>/instagrams (External)
    @detail_route(methods=['get'], url_path='instagrams',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def instagrams(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        instagram_posts = []
        if contact.instagram != '':
            limit, offset = get_pagination(request)
            query = {
                'size': limit,
                'from': offset,
                'query': {
                    'bool': {
                        'should': [{
                            'term': {
                                'data.Username': contact.instagram
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
                }]
            }

            es_instagrams = es.search(
                index='instagrams', doc_type='instagram', body=query)
            if 'hits' in es_instagrams and 'hits' in es_instagrams['hits']:
                for es_instagram in es_instagrams['hits']['hits']:
                    if ('_source' in es_instagram and
                            'data' in es_instagram['_source']):
                        es_instagram = format_es_response(es_instagram)
                        es_instagram['type'] = 'instagrams'
                        instagram_posts.append(es_instagram['_source']['data'])

        return BulkResponse(instagram_posts, {}, len(instagram_posts),
                            len(instagram_posts))

    # GET /contacts/<id>/instagramprofile (External)
    @detail_route(methods=['get'], url_path='instagramprofile',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def instagram_profile(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        instagram_profile = {}
        if contact.instagram != '':
            query = {
                'query': {
                    'bool': {
                        'must': [{
                            'term': {
                                'data.Username': contact.instagram
                            }
                        }]
                    }
                }
            }

            es_instagram_profile = es.search(
                index='instagrams', doc_type='user', body=query)
            if ('hits' in es_instagram_profile and
                    'hits' in es_instagram_profile['hits']):
                if len(es_instagram_profile['hits']['hits']) > 0:
                    instagram_profile = es_instagram_profile[
                        'hits']['hits'][0]['_source']['data']

        return Response(instagram_profile, {})

    # GET /contacts/<id>/instagramtimeseries (External)
    @detail_route(methods=['get'], url_path='instagramtimeseries',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def instagram_timeseries(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)

        # Response to user
        instagram_timeseries = []
        total_instagram_timeseries = 0

        if contact.instagram != '':
            query = {
                'query': {
                    'bool': {
                        'must': [{
                            'term': {
                                'data.Username': contact.instagram
                            }
                        }]
                    }
                },
                'sort': [{
                    'data.CreatedAt': {
                        'order': 'desc',
                        'mode': 'avg'
                    }
                }]
            }

            es_instagram_timeseries = es.search(
                index='timeseries', doc_type='instagram', body=query)

            if ('hits' in es_instagram_timeseries and
                    'total' in es_instagram_timeseries['hits']):
                total_instagram_timeseries = es_instagram_timeseries[
                    'hits']['total']

            if ('hits' in es_instagram_timeseries and
                    'hits' in es_instagram_timeseries['hits']):
                for ts in es_instagram_timeseries['hits']['hits']:
                    if ('_source' in ts and 'data' in ts['_source']):
                        # ts = format_es_response(ts)
                        instagram_timeseries.append(ts['_source']['data'])

        return BulkResponse(instagram_timeseries, {},
                            len(instagram_timeseries),
                            total_instagram_timeseries)

    # GET /contacts/<id>/feeds (External)
    @detail_route(methods=['get'], url_path='feeds',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def feeds(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        feeds = Feed.objects.filter(
            contact=contact)

        serializer = FeedSerializer(feeds, many=True)
        return BulkResponse(serializer.data, {},
                            len(serializer.data), len(serializer.data))

    # GET /contacts/<id>/emails (External)
    @detail_route(methods=['get'], url_path='emails',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def emails(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        user_profile = UserProfile.objects.get(user=request.user)
        queryset = Email.objects.filter(
            team=user_profile.team,
            to=contact.email,
            is_sent=True,
            delivered=True
        ).order_by('-created')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EmailSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = EmailSerializer(queryset, many=True)
        return BulkResponse(serializer.data, {},
                            len(serializer.data), len(serializer.data))

    # GET /contacts/<id>/lists (External)
    @detail_route(methods=['get'], url_path='lists',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def lists(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        user_profile = UserProfile.objects.get(user=request.user)
        queryset = MediaList.objects.filter(
            contacts=contact, team=user_profile.team,
            archived=False).order_by('-created')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MediaListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MediaListSerializer(queryset, many=True)
        return BulkResponse(serializer.data, {},
                            len(serializer.data), len(serializer.data))

    # GET /contacts/<id>/enrich (External)
    @detail_route(methods=['get'], url_path='enrich',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def enrich(self, request, pk=None):
        return

    # POST /contacts/<id>/add-tags (External)
    @detail_route(methods=['post'], url_path='add-tags',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def add_tags(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        if 'tags' in request.data:
            for tag in request.data['tags']:
                contact.tags.add(tag)
                contact.save()

            serializer = ContactSerializer(contact)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /contacts/<id>/remove-tags (External)
    @detail_route(methods=['post'], url_path='remove-tags',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def remove_tags(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        if 'tags' in request.data:
            for tag in request.data['tags']:
                contact.tags.remove(tag)
                contact.save()

            serializer = ContactSerializer(contact)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /contacts/<id>/add-employers (External)
    @detail_route(methods=['post'], url_path='add-employers',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def add_employers(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        if 'employers' in request.data:
            for employer_id in request.data['employers']:
                try:
                    publication = Publication.objects.get(pk=employer_id)
                    contact.employers.add(publication)
                    contact.save()
                except Publication.DoesNotExist:
                    continue

            serializer = ContactSerializer(contact)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /contacts/<id>/remove-employers
    @detail_route(methods=['post'], url_path='remove-employers',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def remove_employers(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        if 'employers' in request.data:
            for employer_id in request.data['employers']:
                try:
                    publication = Publication.objects.get(pk=employer_id)
                    contact.employers.remove(publication)
                    contact.save()
                except Publication.DoesNotExist:
                    continue

            serializer = ContactSerializer(contact)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /contacts/<id>/add-past-employers (External)
    @detail_route(methods=['post'], url_path='add-past-employers',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def add_past_employers(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        if 'employers' in request.data:
            for employer_id in request.data['employers']:
                try:
                    publication = Publication.objects.get(pk=employer_id)
                    contact.past_employers.add(publication)
                    contact.save()
                except Publication.DoesNotExist:
                    continue

            serializer = ContactSerializer(contact)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /contacts/<id>/remove-past-employers (External)
    @detail_route(methods=['post'], url_path='remove-past-employers',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def remove_past_employers(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        if 'employers' in request.data:
            for employer_id in request.data['employers']:
                try:
                    publication = Publication.objects.get(pk=employer_id)
                    contact.past_employers.remove(publication)
                    contact.save()
                except Publication.DoesNotExist:
                    continue

            serializer = ContactSerializer(contact)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /contacts/<id>/add-to-list (External)
    @detail_route(methods=['post'], url_path='add-to-list',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def add_to_lists(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        if 'listids' in request.data:
            for list_id in request.data['listids']:
                try:
                    media_list = MediaList.objects.get(pk=list_id)
                    media_list.contacts.add(contact)
                    media_list.save()
                except MediaList.DoesNotExist:
                    continue

            serializer = ContactSerializer(contact)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /contacts/<id>/remove-from-list (External)
    @detail_route(methods=['post'], url_path='remove-from-list',
                  permission_classes=[IsAuthenticated, IsAdminOrIsSelf])
    def remove_from_lists(self, request, pk=None):
        contact = self.get_contact_by_pk(request, pk)
        if 'listids' in request.data:
            for list_id in request.data['listids']:
                try:
                    media_list = MediaList.objects.get(pk=list_id)
                    media_list.contacts.remove(contact)
                    media_list.save()
                except MediaList.DoesNotExist:
                    continue

            serializer = ContactSerializer(contact)
            return Response(serializer.data, {})
        raise ParseError()
