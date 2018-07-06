# -*- coding: utf-8 -*-
# Third-party app imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import OrderingFilter

# Imports from app
from tabulae.apps.general.viewset import NewsAIModelViewSet
from .models import DatabasePublication
from .permissions import DatabasePublicationPermission
from .serializers import DatabasePublicationSerializer


class DatabasePublicationViewSet(NewsAIModelViewSet):
	queryset = DatabasePublication.objects.all()
	serializer_class = DatabasePublicationSerializer
	permission_classes = (DatabasePublicationPermission,)
	filter_backends = (OrderingFilter,)
	paginate_by_param = 'limit'
	ordering_fields = '__all__'
