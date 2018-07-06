# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# Third-party app imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import NotAuthenticated, ParseError

# Imports from app
from tabulae.apps.general.viewset import NewsAIModelViewSet
from tabulae.apps.general.response import Response, BulkResponse
from .models import Template
from .serializers import TemplateSerializer
from .permissions import TemplatePermission


class TemplateViewSet(NewsAIModelViewSet):
    serializer_class = TemplateSerializer
    permission_classes = (TemplatePermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    ordering_fields = ('created',)

    def get_template_by_pk(self, request, pk):
        # Switch to team__pk=request.user.team.pk
        queryset = Template.objects.filter(created_by=request.user)
        template = get_object_or_404(queryset, pk=pk)
        return template

    def retrieve(self, request, pk=None):
        if request.user and request.user.is_authenticated():
            template = self.get_template_by_pk(request, pk)
            serializer = TemplateSerializer(template)
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
            return (
                Template.objects.filter(
                    created_by=self.request.user).order_by('-created'))
        raise NotAuthenticated()

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']

            if isinstance(data, list):
                kwargs['many'] = True

        return super(TemplateViewSet, self).get_serializer(*args, **kwargs)
