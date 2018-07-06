# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model
from django.db import models

# Third-party app imports
from taggit_serializer.serializers import (
    TagListSerializerField,
    TaggitSerializer,
)
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    IntegerField,
    BooleanField,
)
from rest_framework.serializers import CharField

# Imports from app
from tabulae.apps.general.response import form_response
from tabulae.apps.users.models import Client, UserProfile
from .models import MediaList, CustomFieldsMap


class CustomFieldsMapSerializer(ModelSerializer):

    id = IntegerField(required=False)

    customfield = BooleanField(source='custom_field', required=False)
    custom_field = BooleanField(required=False)

    def _internal_field(self, obj):
        internal_fields = [
            'employers',
            'pastemployers'
        ]

        if obj.value in internal_fields:
            return True

        return False

    def _read_only_field(self, obj):
        read_only_fields = [
            'instagramfollowers',
            'instagramfollowing',
            'instagramlikes',
            'instagramcomments',
            'instagramposts',
            'twitterfollowers',
            'twitterfollowing',
            'twitterlikes',
            'twitterretweets',
            'twitterposts'
        ]

        if obj.value in read_only_fields:
            return True

        return False

    def _get_description(self, obj):
        daily_description_fields = [
            'instagramfollowers',
            'instagramfollowing',
            'instagramlikes',
            'instagramcomments',
            'instagramposts',
            'twitterfollowers',
            'twitterfollowing',
            'twitterlikes',
            'twitterretweets',
            'twitterposts',
            'latestheadline'
        ]

        if obj.value in daily_description_fields:
            return 'Updated on a daily basis'

        return ''

    def _get_type(self, obj):
        if obj.value == 'lastcontacted':
            return 'Date'

        return 'String'

    def to_representation(self, obj):
        custom_fields_map = {
            'id': obj.pk,
            'type': 'fields-map',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'name': obj.name,
            'value': obj.value,
            'customfield': obj.custom_field,
            'hidden': obj.hidden,
            'internal': self._internal_field(obj),
            'readonly': self._read_only_field(obj),
            'description': self._get_description(obj),
            'type': self._get_type(obj)
        }

        return custom_fields_map

    class Meta:
        model = CustomFieldsMap
        fields = ('name', 'value', 'custom_field', 'hidden', 'id',
                  'customfield',)


class MediaListSerializer(TaggitSerializer, ModelSerializer):
    tags = TagListSerializerField(required=False)

    # These two are to properly serialize the fields_maps.
    # We want to return the right fieldsmap.
    # The second one is so we can write 'fieldsmap' in POST
    # request rather than 'fields_map'.
    fields_map = CustomFieldsMapSerializer(many=True, required=False)
    fieldsmap = CustomFieldsMapSerializer(
        source='fields_map', many=True, required=False)

    # Client
    client = CharField(
        source='client_name', required=False)
    client_name = CharField(required=False)

    def to_representation(self, obj):
        has_data = False
        included = {}
        if isinstance(obj, dict):
            if 'data' in obj and 'included' in obj:
                has_data = True
                included = obj['included']

                obj = obj['data']

        media_list = {
            'id': obj.pk,
            'type': 'lists',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'name': obj.name,
            'client': obj.client_name,
            'clients': (obj.clients and
                        obj.clients.values_list('id', flat=True)),

            'contacts': (obj.contacts and
                         obj.contacts.values_list('id', flat=True)),
            'fieldsmap': (obj.fields_map and
                          CustomFieldsMapSerializer(
                              obj.fields_map, many=True).data),
            'tags': (obj.tags and obj.tags.values_list('name', flat=True)),

            'fileupload': obj.file and obj.file.pk,
            'teamid': obj.team and obj.team.pk,

            'readonly': False,
            'publiclist': obj.public_list,
            'archived': obj.archived,
            'subscribed': obj.subscribed,
            'isdeleted': obj.is_deleted,
        }

        if has_data:
            return {
                'data': media_list,
                'included': included,
            }

        return media_list

    def _generate_fields_map(self, user):
        first_name = CustomFieldsMap(
            name='First Name', value='firstname',
            custom_field=False, hidden=False,
            created_by=user,)

        last_name = CustomFieldsMap(
            name='Last Name', value='lastname',
            custom_field=False, hidden=False,
            created_by=user,)

        email = CustomFieldsMap(
            name='Email', value='email',
            custom_field=False, hidden=False,
            created_by=user,)

        employers = CustomFieldsMap(
            name='Employers', value='employers',
            custom_field=False, hidden=False,
            created_by=user,)

        past_employers = CustomFieldsMap(
            name='Past Employers', value='pastemployers',
            custom_field=False, hidden=False,
            created_by=user,)

        notes = CustomFieldsMap(
            name='Notes', value='notes',
            custom_field=False, hidden=False,
            created_by=user,)

        twitter = CustomFieldsMap(
            name='Twitter', value='twitter',
            custom_field=False, hidden=False,
            created_by=user,)

        linkedin = CustomFieldsMap(
            name='Linkedin', value='linkedin',
            custom_field=False, hidden=False,
            created_by=user,)

        instagram = CustomFieldsMap(
            name='Instagram', value='instagram',
            custom_field=False, hidden=False,
            created_by=user,)

        website = CustomFieldsMap(
            name='Website', value='website',
            custom_field=False, hidden=False,
            created_by=user,)

        blog = CustomFieldsMap(
            name='Blog', value='blog',
            custom_field=False, hidden=False,
            created_by=user,)

        phone_number = CustomFieldsMap(
            name='Phone #', value='phonenumber',
            custom_field=False, hidden=False,
            created_by=user,)

        location = CustomFieldsMap(
            name='Location', value='location',
            custom_field=False, hidden=False,
            created_by=user,)

        instagram_followers = CustomFieldsMap(
            name='Instagram Followers', value='instagramfollowers',
            custom_field=True, hidden=True,
            created_by=user,)

        instagram_following = CustomFieldsMap(
            name='Instagram Following', value='instagramfollowing',
            custom_field=True, hidden=True,
            created_by=user,)

        instagram_likes = CustomFieldsMap(
            name='Instagram Likes', value='instagramlikes',
            custom_field=True, hidden=True,
            created_by=user,)

        instagram_comments = CustomFieldsMap(
            name='Instagram Comments', value='instagramcomments',
            custom_field=True, hidden=True,
            created_by=user,)

        instagram_posts = CustomFieldsMap(
            name='Instagram Posts', value='instagramposts',
            custom_field=True, hidden=True,
            created_by=user,)

        # Twitter
        twitter_followers = CustomFieldsMap(
            name='Twitter Followers', value='twitterfollowers',
            custom_field=True, hidden=True,
            created_by=user,)

        twitter_following = CustomFieldsMap(
            name='Twitter Following', value='twitterfollowing',
            custom_field=True, hidden=True,
            created_by=user,)

        twitter_likes = CustomFieldsMap(
            name='Twitter Likes', value='twitterlikes',
            custom_field=True, hidden=True,
            created_by=user,)

        twitter_retweets = CustomFieldsMap(
            name='Twitter Reweets', value='twitterretweets',
            custom_field=True, hidden=True,
            created_by=user,)

        twitter_posts = CustomFieldsMap(
            name='Twitter Posts', value='twitterposts',
            custom_field=True, hidden=True,
            created_by=user,)

        latest_headline = CustomFieldsMap(
            name='Latest Headline', value='latestheadline',
            custom_field=True, hidden=True,
            created_by=user,)

        last_contacted = CustomFieldsMap(
            name='Last Contacted', value='lastcontacted',
            custom_field=True, hidden=True,
            created_by=user,)

        publication_last_contacted = CustomFieldsMap(
            name='Publication Last Contacted',
            value='publicationlastcontacted',
            custom_field=True, hidden=True,
            created_by=user,)

        fields_map = [first_name, last_name, email, employers, past_employers,
                      notes, twitter, linkedin, instagram, website, blog,
                      phone_number, location, instagram_followers,
                      instagram_following, instagram_likes, instagram_comments,
                      instagram_posts, twitter_followers, twitter_following,
                      twitter_likes, twitter_retweets, twitter_posts,
                      latest_headline, last_contacted,
                      publication_last_contacted]

        fields = CustomFieldsMap.objects.bulk_create(fields_map)

        return fields

    def create(self, data):
        clients = None
        contacts = []
        fields_map = []
        file = None
        team = None
        tags = []

        if 'clients' in data:
            clients = data.pop('clients')

        if 'contacts' in data:
            contacts = data.pop('contacts')

        if 'fields_map' in data:
            fields_map = data.pop('fields_map')

        if 'file' in data:
            file = data.pop('file')

        if 'team' in data:
            team = data.pop('team')

        if 'tags' in data:
            tags = data.pop('tags')

        # Add user as the creator of media list
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

        # Create media list
        media_list = MediaList.objects.create(**data)

        # If there is a client
        if clients:
            media_list.clients = clients

        # Add contacts to list
        if len(contacts) > 0:
            media_list.contacts.set(contacts)

        fields = self._generate_fields_map(user)
        media_list.fields_map.set(fields)

        # Add fields_map to list
        if len(fields_map) > 0:
            for field_map in fields_map:
                # Here check to see if it's already been created
                custom_fields_map = CustomFieldsMap.objects.create(
                    created_by=user, **field_map)
                media_list.fields_map.add(custom_fields_map)

        # Add file to list
        if file:
            media_list.file = file

        # Add tags to list
        if len(tags) > 0:
            for tag in tags:
                media_list.tags.add(tag)

        user_profile = UserProfile.objects.get(user=user)
        media_list.team = user_profile.team
        media_list.created_by = user
        media_list.save()

        return media_list

    def update(self, media_list, validated_data):
        media_list.name = validated_data.get(
            'name', media_list.name)
        media_list.client_name = validated_data.get(
            'client_name', media_list.client_name)

        if 'clients' in validated_data:
            media_list.clients = validated_data['clients']

        if 'contacts' in validated_data:
            contacts = validated_data['contacts']
            media_list.contacts.set(contacts)

        # Add user as the creator of media list
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

        if 'fields_map' in validated_data:
            order = 1
            order_array = []
            for field_map in validated_data['fields_map']:
                if 'id' in field_map:
                    try:
                        custom_fields_map = CustomFieldsMap.objects.get(
                            pk=field_map['id'])
                        custom_fields_map.name = field_map.get(
                            'name', custom_fields_map.name)
                        custom_fields_map.value = field_map.get(
                            'value', custom_fields_map.value)
                        custom_fields_map.custom_field = field_map.get(
                            'custom_field', custom_fields_map.custom_field)
                        custom_fields_map.hidden = field_map.get(
                            'hidden', custom_fields_map.hidden)
                        custom_fields_map.order = order
                        custom_fields_map.save()

                        order_array.append(custom_fields_map)

                    except CustomFieldsMap.DoesNotExist:
                        continue
                else:
                    custom_fields_map = CustomFieldsMap.objects.create(
                        created_by=user,
                        order=order, **field_map)
                    media_list.fields_map.add(custom_fields_map)
                    order_array.append(custom_fields_map)
                order += 1
            media_list.fields_map.set(order_array)

        # Pass this. They can use the /lists/<id>/add-tags endpoint
        if 'tags' in validated_data:
            for tag in validated_data['tags']:
                media_list.tags.add(tag)

        if 'file' in validated_data:
            media_list.file = validated_data['file']

        if 'team' in validated_data:
            media_list.team = validated_data['team']

        media_list.public_list = validated_data.get(
            'public_list', media_list.public_list)
        media_list.archived = validated_data.get(
            'archived', media_list.archived)
        media_list.subscribed = validated_data.get(
            'subscribed', media_list.subscribed)
        media_list.is_deleted = validated_data.get(
            'is_deleted', media_list.is_deleted)

        user_profile = UserProfile.objects.get(user=user)
        media_list.team = user_profile.team

        media_list.save()

        return form_response(media_list, {})

    class Meta:
        model = MediaList
        fields = ('name', 'client_name', 'client', 'clients',
                  'contacts', 'fields_map', 'tags', 'file',
                  'team', 'public_list', 'archived',
                  'subscribed', 'is_deleted', 'fieldsmap')
