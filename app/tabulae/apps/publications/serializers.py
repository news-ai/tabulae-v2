# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model

# Third-party app imports
from rest_framework.serializers import ModelSerializer

# Imports from app
from tabulae.apps.general.response import form_response
from .models import Publication


class PublicationSerializer(ModelSerializer):

    def to_representation(self, obj):
        has_data = False
        included = {}
        if isinstance(obj, dict):
            if 'data' in obj and 'included' in obj:
                has_data = True
                included = obj['included']

                obj = obj['data']

        publication = {
            'id': obj.pk,
            'type': 'publications',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'name': obj.name,
            'url': obj.url,

            'linkedin': obj.linkedin,
            'twitter': obj.twitter,
            'instagram': obj.instagram,
            'websites': obj.websites and obj.websites.values(),
            'blog': obj.blog,

            'verified': obj.verified,
        }

        if has_data:
            return {
                'data': publication,
                'included': included,
            }

        return publication

    def create(self, data):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

        publication = Publication.objects.create(**data)
        publication.created_by = user
        publication.save()

        return publication

    def update(self, publication, validated_data):
        publication.name = validated_data.get(
            'name', contact.name)
        publication.url = validated_data.get(
            'url', contact.url)

        publication.linkedin = validated_data.get(
            'linkedin', contact.linkedin)
        publication.twitter = validated_data.get(
            'twitter', contact.twitter)
        publication.instagram = validated_data.get(
            'instagram', contact.instagram)
        publication.websites = validated_data.get(
            'websites', contact.websites)
        publication.blog = validated_data.get(
            'blog', contact.blog)

        publication.verified = validated_data.get(
            'verified', contact.verified)

        publication.save()
        return form_response(publication, {})

    class Meta:
        model = Publication
        fields = ('name', 'url', 'linkedin', 'twitter',
                          'instagram', 'websites', 'blog', 'verified')
