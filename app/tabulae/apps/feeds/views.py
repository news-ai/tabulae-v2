# -*- coding: utf-8 -*-
# Stdlib imports
import datetime

# Core Django imports
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# Third-party app imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import OrderingFilter
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView
from rest_framework.exceptions import NotAuthenticated

# Imports from app
from tabulae.apps.general.viewset import NewsAIModelViewSet
from tabulae.apps.general.response import Response, BulkResponse
from tabulae.apps.general.elastic_search import es
from tabulae.apps.general.permissions import IsAdminOrIsSelf
from tabulae.apps.users.models import UserProfile
from .models import Feed
from .serializers import FeedSerializer
from .permissions import FeedPermission


class FeedViewSet(NewsAIModelViewSet):
    queryset = Feed.objects.all()
    serializer_class = FeedSerializer
    permission_classes = (FeedPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    paginate_by_param = 'limit'
    ordering_fields = '__all__'

    def get_feed_by_pk(self, request, pk):
        # Switch to team__pk=request.user.team.pk
        queryset = Feed.objects.all()
        feed = get_object_or_404(queryset, pk=pk)
        return feed

    def retrieve(self, request, pk=None):
        if request.user and request.user.is_authenticated():
            feed = self.get_feed_by_pk(request, pk)
            serializer = FeedSerializer(feed)
            return Response(serializer.data, {})
        raise NotAuthenticated()

    def list(self, request):
        queryset = Feed.objects.filter(
            created_by=self.request.user).order_by('-created')
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return BulkResponse(serializer.data, {},
                            len(serializer.data), len(serializer.data))

    def get_queryset(self,):
        if self.request.user and self.request.user.is_authenticated():
            return (
                Feed.objects.all().order_by('-created'))
        raise NotAuthenticated()

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']

            if isinstance(data, list):
                kwargs['many'] = True

        return super(FeedViewSet, self).get_serializer(*args, **kwargs)
