# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model

# Third-party app imports
from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    CharField,
    ListField,
)
# Imports from app
from tabulae.apps.general.response import form_response
from tabulae.apps.general.serializers import DynamicFieldsModelSerializer
from tabulae.apps.lists.models import MediaList
from tabulae.apps.templates.models import Template
from tabulae.apps.contacts.models import Contact
from tabulae.apps.files.models import File
from tabulae.apps.users.models import Client, Team, UserProfile
from .models import Email, Campaign


class CampaignSerializer(ModelSerializer):

    def _percentage(self, part, whole):
        if whole == 0:
            return 0
        return 100 * (float(part)/float(whole))

    def to_representation(self, obj):
        show = True
        if obj.delivered == 0:
            show = False

        campaign = {
            'id': obj.pk,
            'type': 'campaigns',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'date': '',
            'subject': obj.subject,
            'userid': obj.created_by and obj.created_by.pk,
            'baseSubject': '',
            'delivered': obj.delivered,

            # Opens
            'opens': obj.opens,
            'uniqueOpens': obj.unique_opens,
            'uniqueOpensPercentage': self._percentage(
                obj.unique_opens, obj.delivered),

            # clicks
            'clicks': obj.clicks,
            'uniqueClicks': obj.unique_clicks,
            'uniqueClicksPercentage': self._percentage(
                obj.unique_clicks, obj.delivered),

            # Replies
            'uniqueReplies': obj.unique_replies,
            'uniqueRepliesPercentage': self._percentage(
                obj.unique_replies, obj.delivered),

            'bounces': obj.bounces,
            'isscheduled': False,
            'show': show
        }

        return campaign

    class Meta:
        model = Campaign


class EmailSerializer(ModelSerializer):

    list_in = PrimaryKeyRelatedField(
        queryset=MediaList.objects.all(),
        required=False,
        write_only=False,
        allow_null=True)
    listid = PrimaryKeyRelatedField(
        source='list_in',
        queryset=MediaList.objects.all(),
        required=False,
        write_only=False,
        allow_null=True)

    contact = PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        required=False,
        write_only=False,
        allow_null=True)
    contactid = PrimaryKeyRelatedField(
        source='contact',
        queryset=Contact.objects.all(),
        required=False,
        write_only=False,
        allow_null=True)

    client = PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        required=False,
        write_only=False,
        allow_null=True)
    clientid = PrimaryKeyRelatedField(
        source='client',
        queryset=Client.objects.all(),
        required=False,
        write_only=False,
        allow_null=True)

    template = PrimaryKeyRelatedField(
        queryset=Template.objects.all(),
        required=False,
        write_only=False,
        allow_null=True)
    templateid = PrimaryKeyRelatedField(
        source='template',
        queryset=Template.objects.all(),
        required=False,
        write_only=False,
        allow_null=True)

    fromemail = CharField(
        source='from_email',
        required=False,
        allow_blank=True)
    from_email = CharField(
        required=False,
        allow_null=True,
        allow_blank=True)

    sender = CharField(
        required=False,
        allow_null=True,
        allow_blank=True)
    to = CharField(
        required=False,
        allow_null=True,
        allow_blank=True)
    subject = CharField(
        required=False,
        allow_null=True,
        allow_blank=True)

    baseSubject = CharField(
        source='base_subject',
        required=False,
        allow_null=True,
        allow_blank=True)
    base_subject = CharField(
        required=False,
        allow_null=True,
        allow_blank=True)

    body = CharField(
        required=False,
        allow_null=True,
        allow_blank=True)

    cc = ListField(
        source='CC',
        child=CharField(),
        required=False)
    bcc = ListField(
        source='BCC',
        child=CharField(),
        required=False)

    firstname = CharField(
        source='first_name',
        required=False,
        allow_null=True,
        allow_blank=True)
    first_name = CharField(
        required=False,
        allow_null=True,
        allow_blank=True)

    lastname = CharField(
        source='last_name',
        required=False,
        allow_null=True,
        allow_blank=True)
    last_name = CharField(
        required=False,
        allow_null=True,
        allow_blank=True)

    attachments = PrimaryKeyRelatedField(
        queryset=File.objects.all(),
        required=False,
        many=True,
        write_only=False,
        allow_null=True)

    def to_representation(self, obj):
        has_data = False
        included = {}
        if isinstance(obj, dict):
            if 'data' in obj and 'included' in obj:
                has_data = True
                included = obj['included']

                obj = obj['data']

        email = {
            'id': obj.pk,
            'type': 'emails',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'method': obj.method,

            'listid': obj.list_in and obj.list_in.pk,
            'contactid': obj.contact and obj.contact.pk,
            'clientid': obj.client and obj.client.pk,
            'templateid': obj.template and obj.template.pk,

            'fromemail': obj.from_email,

            'campaign': obj.campaign and obj.campaign.pk,

            'sender': obj.sender,
            'to': obj.to,
            'subject': obj.subject,
            'baseSubject': obj.base_subject,
            'body': obj.body,

            'cc': obj.CC,
            'bcc': obj.BCC,

            'firstname': obj.first_name,
            'lastname': obj.last_name,

            'sendat': obj.send_at,

            'sendgridid': obj.sendgrid_id,

            'nylasid': obj.nylas_id,
            'nylasthreadid': obj.nylas_thread_id,

            'teamid': obj.team and obj.team.pk,

            'attachments': obj.attachments and obj.attachments.values_list(
                    'id', flat=True),

            'delivered': obj.delivered,
            'bouncedreason': obj.bounced_reasons,
            'bounced': obj.bounced,
            'clicked': obj.clicked,
            'opened': obj.opened,
            'spam': obj.spam,
            'cancel': obj.cancel,
            'dropped': obj.dropped,

            'sendgridopened': obj.sendgrid_opened,
            'sendgridclicked': obj.sendgrid_clicked,

            'archived': obj.archived,
            'issent': obj.is_sent,
        }

        if has_data:
            return {
                'data': email,
                'included': included,
            }

        return email

    def create(self, data):
        list_in = None
        template = None
        contact = None
        client = None
        team = None
        attachments = []

        if 'list_in' in data:
            list_in = data.pop('list_in')

        if 'template' in data:
            template = data.pop('template')

        if 'contact' in data:
            contact = data.pop('contact')

        if 'client' in data:
            client_id = data.pop('client')

        if 'team' in data:
            team = data.pop('team')

        if 'attachments' in data:
            attachments = data.pop('attachments')

        email = Email.objects.create(**data)

        if list_in:
            email.list_in = list_in

        if template:
            email.template = template

        if contact:
            email.contact = contact

        if client:
            email.client = client

        if len(attachments) > 0:
            email.attachments.set(attachments)

        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

        user_profile = UserProfile.objects.get(user=user)
        email.method = user_profile.get_user_email_provider()
        email.team = user_profile.team
        email.created_by = user
        email.save()

        return email

    def update(self, email, validated_data):
        email.method = validated_data.get(
            'method', email.method)

        if 'list_in' in validated_data:
            email.list_in = validated_data['list_in']

        if 'template' in validated_data:
            email.template = validated_data['template']

        if 'contact' in validated_data:
            email.contact = validated_data['contact']

        if 'client' in validated_data:
            email.client = validated_data['client']

        email.from_email = validated_data.get(
            'from_email', email.from_email)

        email.sender = validated_data.get(
            'sender', email.sender)
        email.to = validated_data.get(
            'to', email.to)
        email.subject = validated_data.get(
            'subject', email.subject)
        email.base_subject = validated_data.get(
            'base_subject', email.base_subject)
        email.body = validated_data.get(
            'body', email.body)

        email.CC = validated_data.get(
            'CC', email.CC)
        email.BCC = validated_data.get(
            'BCC', email.BCC)

        email.first_name = validated_data.get(
            'first_name', email.first_name)
        email.last_name = validated_data.get(
            'last_name', email.last_name)

        email.send_at = validated_data.get(
            'send_at', email.send_at)

        if 'team' in validated_data:
            email.team = validated_data['team']

        # Pass this. They can use the /emails/<id>/add-attachments endpoint
        if 'attachments' in validated_data:
            email.attachments.set(attachments)

        email.delivered = validated_data.get(
            'delivered', email.delivered)
        email.bounced_reasons = validated_data.get(
            'bounced_reasons', email.bounced_reasons)
        email.bounced = validated_data.get(
            'bounced', email.bounced)
        email.clicked = validated_data.get(
            'clicked', email.clicked)
        email.opened = validated_data.get(
            'opened', email.opened)
        email.spam = validated_data.get(
            'spam', email.spam)
        email.cancel = validated_data.get(
            'cancel', email.cancel)
        email.dropped = validated_data.get(
            'dropped', email.dropped)

        email.sendgrid_opened = validated_data.get(
            'sendgrid_opened', email.sendgrid_opened)
        email.sendgrid_clicked = validated_data.get(
            'sendgrid_clicked', email.sendgrid_clicked)

        email.archived = validated_data.get(
            'archived', email.archived)

        email.is_sent = validated_data.get(
            'is_sent', email.is_sent)

        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

        user_profile = UserProfile.objects.get(user=user)
        email.method = user_profile.get_user_email_provider()
        email.team = user_profile.team
        email.save()

        return form_response(email, {})

    class Meta:
        model = Email
        fields = ('method', 'list_in', 'template',
                  'contact', 'client', 'from_email', 'sender',
                  'to', 'subject', 'base_subject', 'body',
                  'CC', 'BCC', 'first_name', 'last_name',
                  'send_at', 'team', 'attachments', 'delivered',
                  'bounced_reasons', 'bounced', 'clicked', 'opened',
                  'spam', 'cancel', 'dropped', 'sendgrid_opened',
                  'sendgrid_clicked', 'archived', 'is_sent',
                  'cc', 'bcc', 'clientid', 'contactid', 'listid',
                  'templateid', 'baseSubject', 'firstname',
                  'lastname', 'fromemail', 'campaign',)
