# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model

# Third-party app imports
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    EmailField,
    Field,
    PrimaryKeyRelatedField,
    CharField,
    BooleanField,
    DateTimeField,
    IntegerField,
)

# Imports from app
from tabulae.apps.general.response import form_response
from tabulae.apps.publications.serializers import PublicationSerializer
from tabulae.apps.publications.models import Publication
from tabulae.apps.lists.models import MediaList
from tabulae.apps.users.serializers import TeamSerializer
from tabulae.apps.users.models import Client, Team, UserProfile
from .models import Contact, CustomContactField


class CustomContactFieldSerializer(ModelSerializer):

    id = IntegerField(required=False)

    def to_representation(self, obj):
        custom_field = {
            'name': obj.name,
            'value': obj.value
        }

        return custom_field

    class Meta:
        model = CustomContactField
        fields = ('name', 'value', 'id',)


class ContactSerializer(TaggitSerializer, ModelSerializer):

    firstname = CharField(source='first_name',
                          required=False, allow_blank=True)
    first_name = CharField(required=False, allow_null=True,
                           allow_blank=True)

    lastname = CharField(source='last_name', required=False,
                         allow_blank=True)
    last_name = CharField(required=False, allow_null=True,
                          allow_blank=True)

    email = EmailField(required=False, allow_blank=True)

    employers = PrimaryKeyRelatedField(
        queryset=Publication.objects.all(), required=False, many=True,
        write_only=False, allow_null=True)

    pastemployers = PrimaryKeyRelatedField(
        source='past_employers', queryset=Publication.objects.all(),
        required=False, many=True, write_only=False, allow_null=True)
    past_employers = PrimaryKeyRelatedField(
        queryset=Publication.objects.all(), required=False, many=True,
        write_only=False, allow_null=True)

    twitterinvalid = BooleanField(source='twitter_invalid', required=False)
    twitter_invalid = BooleanField(required=False)

    instagraminvalid = BooleanField(source='instagram_invalid', required=False)
    instagram_invalid = BooleanField(required=False)

    twitterprivate = BooleanField(source='twitter_private', required=False)
    twitter_private = BooleanField(required=False)

    instagramprivate = BooleanField(source='instagram_private', required=False)
    instagram_private = BooleanField(required=False)

    phonenumber = CharField(source='phone_number', required=False,
                            allow_blank=True)
    phone_number = CharField(required=False, allow_blank=True)

    customfields = CustomContactFieldSerializer(
        source='custom_fields', many=True, required=False)
    custom_fields = CustomContactFieldSerializer(many=True, required=False)

    isoutdated = BooleanField(source='is_outdated', required=False)
    is_outdated = BooleanField(required=False)

    emailbounced = BooleanField(source='email_bounced', required=False)
    email_bounced = BooleanField(required=False)

    ismastercontact = BooleanField(source='is_master_contact', required=False)
    is_master_contact = BooleanField(required=False)

    isdeleted = BooleanField(source='is_deleted', required=False)
    is_deleted = BooleanField(required=False)

    # Doesn't get added to contact field.
    # Is just there to primarily add a contact to a list
    # automatically when created.
    listid = CharField(required=False, allow_null=True,
                       allow_blank=True)

    tags = TagListSerializerField(required=False)

    teamid = PrimaryKeyRelatedField(
        source='team', queryset=Team.objects.all(),
        required=False, write_only=False, allow_null=True)
    team = PrimaryKeyRelatedField(
        queryset=Team.objects.all(), required=False, write_only=False,
        allow_null=True)

    clientid = PrimaryKeyRelatedField(
        source='client', queryset=Client.objects.all(),
        required=False, write_only=False, allow_null=True)
    client = PrimaryKeyRelatedField(
        queryset=Client.objects.all(), required=False,
        write_only=False, allow_null=True)

    linkedinupdated = DateTimeField(
        source='linkedin_updated', required=False, write_only=False)
    linkedin_updated = DateTimeField(required=False, write_only=False)

    def to_representation(self, obj):
        has_data = False
        included = {}
        if isinstance(obj, dict):
            if 'data' in obj and 'included' in obj:
                has_data = True
                included = obj['included']

                obj = obj['data']

        contact = {
            'id': obj.pk,
            'type': 'contacts',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'firstname': obj.first_name,
            'lastname': obj.last_name,
            'email': obj.email,

            'employers': (obj.employers and
                          obj.employers.values_list('id', flat=True)),
            'notes': obj.notes,
            'pastemployers': (obj.past_employers and
                              obj.past_employers.values_list(
                                  'id', flat=True)),

            'linkedin': obj.linkedin,
            'twitter': obj.twitter,
            'instagram': obj.instagram,
            'websites': obj.websites,
            'blog': obj.blog,

            'twitterinvalid': obj.twitter_invalid,
            'instagraminvalid': obj.instagram_invalid,
            'twitterprivate': obj.twitter_private,
            'instagramprivate': obj.instagram_private,

            'location': obj.location,
            'phonenumber': obj.phone_number,

            'customfields': (obj.custom_fields and
                             obj.custom_fields.values()),

            'isoutdated': obj.is_outdated,
            'emailbounced': obj.email_bounced,

            'ismastercontact': obj.is_master_contact,
            'isdeleted': obj.is_deleted,

            'readonly': False,

            'tags': obj.tags and obj.tags.values(),

            'teamid': obj.team and obj.team.pk,
            'clientid': obj.client and obj.client.pk,

            'linkedinupdated': obj.linkedin_updated,
        }

        if has_data:
            return {
                'data': contact,
                'included': included,
            }

        return contact

    def normalize(self, data):
        if 'email' in data:
            data['email'] = data['email'].lower()

        if 'first_name' in data:
            if data['first_name'].isupper():
                data['first_name'] = data['first_name'].title()

        if 'last_name' in data:
            if data['last_name'].isupper():
                data['last_name'] = data['last_name'].title()

        if 'linkedin' in data:
            data['linkedin'] = data['linkedin'].lower()

        if 'twitter' in data:
            data['twitter'] = data['twitter'].lower()

        # We can't normalize `websites`: we don't exactly know
        # what the URLs could be.

        if 'instagram' in data:
            data['instagram'] = data['instagram'].lower()

        # We can't normalize blog for same reason as websites.

        return data

    def create(self, data):
        employers = []
        past_employers = []
        custom_fields = []
        tags = []
        team = None
        client = None
        list_id = None

        if 'listid' in data:
            list_id = data['listid']
            del data['listid']

        # Normalize the data
        data = self.normalize(data)

        # Get user
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

        # Check if user already exists
        if 'email' in data:
            user_profile = UserProfile.objects.get(user=user)
            try:
                db_contacts = Contact.objects.filter(email=data['email'],
                                                     team=user_profile.team)
                if len(db_contacts) > 0:
                    if list_id:
                        try:
                            media_list = MediaList.objects.get(pk=list_id)
                            media_list.contacts.add(db_contacts[0])
                            media_list.save()
                        except MediaList.DoesNotExist:
                            pass
                    return db_contacts[0]
            except Contact.DoesNotExist:
                pass

        if 'employers' in data:
            employers = data.pop('employers')

        if 'past_employers' in data:
            past_employers = data.pop('past_employers')

        if 'custom_fields' in data:
            custom_fields = data.pop('custom_fields')

        if 'tags' in data:
            tags = data.pop('tags')

        if 'team' in data:
            team = data.pop('team')

        if 'client' in data:
            client = data.pop('client')

        contact = Contact.objects.create(**data)

        if len(employers) > 0:
            contact.employers.set(employers)

        if len(past_employers) > 0:
            contact.past_employers.set(past_employers)

        if len(custom_fields) > 0:
            for custom_field in custom_fields:
                custom_fields_map = CustomContactField.objects.create(
                    created_by=request.user, **custom_field)
                contact.custom_fields.add(custom_fields_map)

        # Add tags to list
        if tags:
            for tag in tags:
                contact.tags.add(tag)

        if client:
            contact.client = client

        user_profile = UserProfile.objects.get(user=user)
        contact.team = user_profile.team
        contact.created_by = user
        contact.save()

        if list_id:
            try:
                media_list = MediaList.objects.get(pk=list_id)
                media_list.contacts.add(contact)
                media_list.save()
            except Contact.DoesNotExist:
                pass

        return contact

    def update(self, contact, validated_data):
        # Get user
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

        contact.first_name = validated_data.get(
            'first_name', contact.first_name)
        contact.last_name = validated_data.get('last_name', contact.last_name)
        contact.email = validated_data.get('email', contact.email)
        contact.notes = validated_data.get('notes', contact.notes)

        # Pass this. They can also use the /contacts/<id>/add-employers
        # endpoint
        if 'employers' in validated_data:
            contact.employers.set(validated_data['employers'])

        # Pass this. They can also use the /contacts/<id>/add-past-employers
        # endpoint
        if 'past_employers' in validated_data:
            contact.past_employers.set(validated_data['past_employers'])

        contact.linkedin = validated_data.get('linkedin', contact.linkedin)
        contact.twitter = validated_data.get('twitter', contact.twitter)
        contact.instagram = validated_data.get('instagram', contact.instagram)
        contact.websites = validated_data.get('websites', contact.websites)
        contact.blog = validated_data.get('blog', contact.blog)

        contact.twitter_invalid = validated_data.get(
            'twitter_invalid', contact.twitter_invalid)
        contact.instagram_invalid = validated_data.get(
            'instagram_invalid', contact.instagram_invalid)

        contact.twitter_private = validated_data.get(
            'twitter_private', contact.twitter_private)
        contact.instagram_private = validated_data.get(
            'instagram_private', contact.instagram_private)

        contact.location = validated_data.get('location', contact.location)
        contact.phone_number = validated_data.get(
            'phone_number', contact.phone_number)

        # Pass this. They can use the /contacts/<id>/add-custom-field endpoint
        if 'custom_fields' in validated_data:
            for custom_field in validated_data['custom_fields']:
                if 'id' in custom_field:
                    # If id is in the custom field
                    # then we update it
                    try:
                        custom_contact_field = CustomContactField.objects.get(
                            pk=custom_field['id'])
                        custom_contact_field.name = custom_field.get(
                            'name', custom_contact_field.name)
                        custom_contact_field.value = custom_field.get(
                            'value', custom_contact_field.value)
                        custom_contact_field.save()
                    except CustomContactField.DoesNotExist:
                        continue
                else:
                    # If there's no id then we create
                    # the custom field
                    custom_contact_field = CustomContactField.objects.create(
                        created_by=user, **custom_field)
                    contact.custom_fields.add(custom_contact_field)

        contact.email_bounced = validated_data.get(
            'email_bounced', contact.email_bounced)

        contact.is_master_contact = validated_data.get(
            'is_master_contact', contact.is_master_contact)
        contact.is_deleted = validated_data.get(
            'is_deleted', contact.is_deleted)

        # Pass this. They can use the /contacts/<id>/add-tags endpoint
        if 'tags' in validated_data:
            for tag in validated_data['tags']:
                contact.tags.add(tag)

        # Overrite the current team association this has
        if 'team' in validated_data:
            contact.team = validated_data['team']

        # Overrite the current client association this has
        if 'client' in validated_data:
            contact.client = validated_data['client']

        contact.linkedin_updated = validated_data.get(
            'linkedin_updated', contact.linkedin_updated)

        user_profile = UserProfile.objects.get(user=user)
        contact.team = user_profile.team
        contact.save()

        return form_response(contact, {})

    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'email', 'employers',
                  'linkedin', 'twitter', 'instagram',
                  'websites', 'blog', 'twitter_invalid', 'instagram_invalid',
                  'twitter_private', 'instagram_private', 'location',
                  'phone_number', 'is_outdated',
                  'email_bounced', 'is_master_contact', 'is_deleted',
                  'tags', 'team', 'client', 'linkedin_updated',
                  'customfields', 'custom_fields', 'clientid',
                  'linkedinupdated', 'teamid', 'isdeleted',
                  'ismastercontact', 'emailbounced', 'isoutdated',
                  'customfields', 'phonenumber', 'instagramprivate',
                  'twitterprivate', 'instagraminvalid', 'twitterinvalid',
                  'pastemployers', 'lastname', 'firstname', 'past_employers',
                  'listid',)
