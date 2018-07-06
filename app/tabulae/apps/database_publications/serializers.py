# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework.serializers import ModelSerializer

# Imports from app
from .models import (
	DatabasePublication
)


class DatabasePublicationSerializer(ModelSerializer):

	def to_representation(self, obj):
		return {
			'id': obj.short_id,
			'type': 'media-publications',
			'name': obj.name,
			'url': obj.url,
		}

	class Meta:
		model = DatabasePublication
