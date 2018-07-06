# -*- coding: utf-8 -*-
# Stdlib imports
from urlparse import urlparse

# Core Django imports
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# Third-party app imports
import requests
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView
from rest_framework.exceptions import NotAuthenticated

# Imports from app
from tabulae.apps.general.viewset import NewsAIModelViewSet
from tabulae.apps.general.response import Response, BulkResponse
from tabulae.apps.general.permissions import IsAdminOrIsSelf
from .models import Publication
from .serializers import PublicationSerializer
from .permissions import PublicationPermission


class PublicationViewSet(NewsAIModelViewSet):
    '''
        left (priority):
        left (not): headlines
    '''
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    permission_classes = (PublicationPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter,)
    paginate_by_param = 'limit'
    ordering_fields = '__all__'
    search_fields = ('name',)

    def get_publication_by_pk(self, request, pk):
        # Switch to team__pk=request.user.team.pk
        queryset = Publication.objects.all()
        publication = get_object_or_404(queryset, pk=pk)
        return publication

    def retrieve(self, request, pk=None):
        if request.user and request.user.is_authenticated():
            publication = self.get_publication_by_pk(request, pk)
            serializer = PublicationSerializer(publication)
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
            return Publication.objects.all()
        raise NotAuthenticated()

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']

            if isinstance(data, list):
                kwargs['many'] = True

        return super(PublicationViewSet, self).get_serializer(*args, **kwargs)

    # GET /publications/<id>/headlines (External - unused)
    @detail_route(methods=['get'], url_path='headlines',
                  permission_classes=[IsAdminOrIsSelf])
    def headlines(self, request, pk=None):
        return

    # GET /publications/<id>/database-profile (External)
    @detail_route(methods=['get'], url_path='database-profile',
                  permission_classes=[IsAdminOrIsSelf])
    def database_profile(self, request, pk=None):
        database_profile = {}
        publication = self.get_publication_by_pk(request, pk)
        if publication.url != '':
            publication_enhance_url = urlparse(publication.url)
            publication_enhance_url = publication_enhance_url.netloc
            r = requests.get(
                ('https://enhance.newsai.org/company/'
                    + publication_enhance_url))
            database_profile = r.json()
            if 'data' in database_profile:
                database_profile = database_profile['data']
        return Response(database_profile, {})

    # GET /publications/<id>/verify (External)
    @detail_route(methods=['get'], url_path='verify',
                  permission_classes=[IsAdminOrIsSelf])
    def verify(self, request, pk=None):
        publication = self.get_publication_by_pk(request, pk)
        publication.verified = True
        publication.save()

        serializer = PublicationSerializer(publication)
        return Response(serializer.data, {})
