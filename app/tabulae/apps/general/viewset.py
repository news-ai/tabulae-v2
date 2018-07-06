# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_201_CREATED

# Imports from app
from .response import Response, BulkResponse


class NewsAIModelViewSet(ModelViewSet):

    def get_paginated_response(self, data, included=[]):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, included)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if isinstance(request.data, list):
            return BulkResponse(serializer.data, [],
                                len(serializer.data),
                                len(serializer.data),
                                status=HTTP_201_CREATED,
                                headers=headers)
        else:
            return Response(serializer.data, {})
