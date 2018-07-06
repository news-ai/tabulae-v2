# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model

# Third-party app imports
from rest_framework.serializers import (
    ModelSerializer,
    URLField,
    BooleanField,
    PrimaryKeyRelatedField,
)

# Imports from app
from tabulae.apps.contacts.serializers import ContactSerializer
from tabulae.apps.contacts.models import Contact
from tabulae.apps.lists.serializers import MediaListSerializer
from tabulae.apps.lists.models import MediaList
from tabulae.apps.publications.serializers import PublicationSerializer
from tabulae.apps.publications.models import Publication
from .models import Feed


class FeedSerializer(ModelSerializer):

    url = URLField(source='feed_url', required=False)
    feed_url = URLField(required=False)

    contactid = PrimaryKeyRelatedField(
        source='contact', queryset=Contact.objects.all(),
        required=False, write_only=False)
    contact = PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        required=False,
        write_only=False)

    listid = PrimaryKeyRelatedField(
        source='list_in', queryset=MediaList.objects.all(),
        required=False, write_only=False)
    list_in = PrimaryKeyRelatedField(
        queryset=MediaList.objects.all(),
        required=False, write_only=False)

    publicationid = PrimaryKeyRelatedField(
        source='publication',
        queryset=Publication.objects.all(),
        required=False, write_only=False)
    publication = PrimaryKeyRelatedField(
        queryset=Publication.objects.all(),
        required=False, write_only=False)

    validfeed = BooleanField(source='valid_feed', required=False)
    valid_feed = BooleanField(required=False)

    running = BooleanField(required=False)

    def to_representation(self, obj):
        has_data = False
        included = {}
        if isinstance(obj, dict):
            if 'data' in obj and 'included' in obj:
                has_data = True
                included = obj['included']

                obj = obj['data']

        feed = {
            'id': obj.pk,
            'type': 'feeds',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'url': obj.feed_url,
            'contactid': obj.contact and obj.contact.pk,
            'publicationid': obj.publication and obj.publication.pk,
            'validfeed': obj.valid_feed,
            'running': obj.running,
        }

        if has_data:
            return {
                'data': feed,
                'included': included,
            }

        return feed

    def create(self, data):
        contact = None
        publication = None

        if 'contact' in data:
            contact = data.pop('contact')

        if 'publication' in data:
            publication = data.pop('publication')

        feed = Feed.objects.create(**data)

        if contact:
            feed.contact = contact

        if publication:
            feed.publication = publication

        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        feed.created_by = user
        feed.save()

        return feed

    class Meta:
        model = Feed
        fields = ('feed_url', 'contact', 'list_in',
                  'publication', 'valid_feed', 'running',
                  'contactid', 'listid', 'publicationid',
                  'validfeed', 'url',)
