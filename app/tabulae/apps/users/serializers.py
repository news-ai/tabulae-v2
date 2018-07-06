# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model
from django.db import models

# Third-party app imports
from social_django.models import UserSocialAuth
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)

# Imports from app
from .models import (
    UserProfile,
    Agency,
    Client,
    Team,
    Invite,
)


class UserLiveTokenSerializer(ModelSerializer):

    def to_representation(self, obj):
        return {
            'token': obj.live_access_token,
        }

    class Meta:
        model = UserProfile


class UserProfileSerializer(ModelSerializer):

    def to_representation(self, obj):
        return {
            'created': obj.created,
            'updated': obj.updated,
            'created_by': obj.created_by,
            'sendgrid_emails': obj.sendgrid_emails,
            'employers': obj.employers.values_list('id', flat=True),
            'team': obj.team,
            'email_signature': obj.email_signature,
            'email_signatures': obj.email_signatures,

            'trial_feedback': obj.trial_feedback,

            'google_id': obj.google_id,

            'outlook': obj.outlook,
            'outlook_username': obj.outlook_username,
            'outlook_microsoft_code': obj.outlook_microsoft_code,

            'gmail': obj.gmail,
            'gmail_nylas_code': obj.gmail_nylas_code,
            'gmail_username': obj.gmail_username,
            'gmail_google_code': obj.gmail_google_code,

            'external_email': obj.external_email,
            'external_email_username': obj.external_email_username,
            'external_email_account_id': obj.external_email_account_id,

            'provider': obj.get_user_email_provider()
        }

    class Meta:
        model = UserProfile
        fields = ('user',)


class UserSerializer(ModelSerializer):
    sendgrid_emails = SerializerMethodField()
    employers = SerializerMethodField()

    def to_representation(self, obj):
        user_profile = UserProfileSerializer(
            UserProfile.objects.get(user=obj)).data

        return {
            # Base
            'id': obj.pk,
            'type': 'users',
            'createdby': user_profile['created_by'],
            'created': obj.date_joined,
            'updated': user_profile['updated'],

            # User profile
            'email': obj.email,
            'firstname': obj.first_name,
            'lastname': obj.last_name,
            'employers': user_profile['employers'],
            'teamid': user_profile['team'] and user_profile['team'].pk,

            # Email signatures
            'emailsignature': user_profile['email_signature'],
            'emailsignatures': user_profile['email_signatures'],

            # Current email provider
            'emailprovider': user_profile['provider'],

            # Sendgrid
            'sendgridemails': user_profile['sendgrid_emails'],

            # Google
            'googleid': user_profile['google_id'],

            # Gmail
            'gmail': user_profile['gmail'],
            'gmailnylasid': user_profile['gmail_nylas_code'],
            'gmailid': user_profile['gmail_google_code'],
            'gmailusernarname': user_profile['gmail_username'],

            # Outlook
            'outlook': user_profile['outlook'],
            'outlookid': user_profile['outlook_microsoft_code'],
            'outlookusername': user_profile['outlook_username'],

            # SMTP
            'externalemail': user_profile['external_email'],
            'externalemailusername': user_profile['external_email_username'],
            'externalemailid': user_profile['external_email_account_id'],

            # Features
            'emailconfirmed': True,
            'getdailyemails': True,
            'mediadatabaseaccess': True,

            'isactive': obj.is_active,
            'isadmin': obj.is_staff,
            'isbanned': False,
            'trialfeedback': user_profile['trial_feedback']
        }

    class Meta:
        UserModel = get_user_model()
        model = UserModel
        fields = ('first_name', 'last_name', 'email',
                  'sendgrid_emails', 'employers',)


class AgencySerializer(ModelSerializer):

    def to_representation(self, obj):
        agency = {
            'id': obj.name,
            'email': obj.email,
            'administrators': obj.administrators.values_list('id', flat=True),
        }

        return agency

    class Meta:
        model = Agency
        fields = ('name', 'email', 'administrators',)


class ClientSerializer(ModelSerializer):

    def to_representation(self, obj):
        client = {
            'id': obj.name,
            'name': obj.name,
            'url': obj.url,
            'notes': obj.notes,
            'tags': obj.tags.values(),

            'agency': obj.agency and obj.agency.pk,

            'linkedin': obj.linkedin,
            'twitter': obj.twitter,
            'instagram': obj.instagram,
            'websites': obj.websites,
            'blog': obj.blog,
        }

        return client

    class Meta:
        model = Client
        fields = ('name', 'url', 'notes', 'tags', 'agency',
                  'linkedin', 'twitter', 'instagram', 'websites', 'blog',)


class TeamSerializer(ModelSerializer):

    def to_representation(self, obj):
        team = {
            'name': obj.name,
            'agency': obj.agency and obj.agency.pk,
            'maxmembers': obj.max_members,
            'members': obj.members.values_list('id', flat=True),
            'admins': obj.admins.values_list('id', flat=True),
        }

        return team

    class Meta:
        model = Team
        fields = ('name', 'agency', 'max_members', 'members', 'admins')


class InviteSerializer(ModelSerializer):

    def to_representation(self, obj):
        invite = {
            'invitecode': obj.invite_code,
            'email': obj.email,
            'isused': obj.is_used,
        }

        return invite

    class Meta:
        model = Invite
        fields = ('invite_code', 'email', 'is_used')
