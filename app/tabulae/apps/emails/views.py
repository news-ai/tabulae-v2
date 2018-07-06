# -*- coding: utf-8 -*-
# Stdlib imports
import datetime
import os
import binascii

# Core Django imports
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# Third-party app imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.status import HTTP_201_CREATED
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.exceptions import NotAuthenticated, ParseError
from rest_framework.parsers import (
    FormParser,
    MultiPartParser,
)

# Imports from app
from tabulae.apps.general.viewset import NewsAIModelViewSet
from tabulae.apps.general.response import Response, BulkResponse
from tabulae.apps.general.permissions import IsAdminOrIsSelf
from tabulae.apps.users.models import UserProfile
from tabulae.apps.files.models import File, EmailImage
from tabulae.apps.files.serializers import EmailImageSerializer, FileSerializer
from .filters import FilterBetweenField
from .models import Email, Campaign
from .serializers import EmailSerializer, CampaignSerializer
from .permissions import EmailPermission
from .tasks import send_sendgrid, send_gmail, send_outlook, send_smtp


class EmailViewSet(NewsAIModelViewSet):
    '''
        left (priority): logs, stats
        left (not)
    '''
    queryset = Email.objects.all()
    serializer_class = EmailSerializer
    permission_classes = (EmailPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter,
                       SearchFilter, FilterBetweenField)
    paginate_by_param = 'limit'
    ordering_fields = '__all__'
    filter_fields = ('subject', 'campaign',)
    filter_field = 'created'

    def _send_emails(self, emails):
        campaign = self._emails_to_campaign(emails)
        for email in emails:
            email.campaign = campaign
            email.is_sent = True
            email.save()

            if email.method == 'sendgrid':
                send_sendgrid.apply_async(
                    args=[email.pk], queue='emails',)
            elif email.method == 'gmail':
                send_gmail.apply_async(
                    args=[email.pk], queue='emails',)
            elif email.method == 'outlook':
                send_outlook.apply_async(
                    args=[email.pk], queue='emails',)
            elif email.method == 'smtp':
                send_smtp.apply_async(
                    args=[email.pk], queue='emails',)

    def _emails_to_campaign(self, emails):
        campaign = None
        if len(emails) > 0:
            first_email = emails[0]

            today = datetime.datetime.now().date()
            tomorrow = today + datetime.timedelta(1)
            today_start = datetime.datetime.combine(today, datetime.time())
            today_end = datetime.datetime.combine(tomorrow, datetime.time())

            campaigns = Campaign.objects.filter(
                created__lte=today_end,
                created__gte=today_start,
                created_by=first_email.created_by,
                subject=first_email.subject)

            if campaigns.count() > 0:
                global campaign

                campaigns = campaigns.all()
                campaign = campaigns[0]

                campaign.delivered += len(emails)
                campaign.save()
            else:
                global campaign

                campaign = Campaign()
                campaign.subject = first_email.subject
                campaign.delivered = len(emails)
                campaign.created_by = first_email.created_by
                campaign.save()
        return campaign

    def _file_to_file_object(self, request):
        attachment_files = []
        for f in request.FILES.getlist('file'):
            attachment_files.append(f)

        files = []
        for attachment_file in attachment_files:
            random_number = binascii.b2a_hex(os.urandom(15))

            original_file_name = attachment_file._name
            file_name = attachment_file._name.replace(' ', '')
            generated_file_name = ''.join(
                [str(request.user.pk), random_number, file_name])
            attachment_file._name = generated_file_name

            file = File(file=attachment_file)
            file.original_name = original_file_name
            file.file_exists = True
            file.file_name = generated_file_name
            file.created_by = request.user
            file.content_type = attachment_file.content_type
            file.save()

            files.append(file)
        return files

    def get_email_by_pk(self, request, pk):
        if self.request.user and self.request.user.is_authenticated():
            queryset = Email.objects.filter(created_by=request.user)
            email = get_object_or_404(queryset, pk=pk)
            return email
        raise NotAuthenticated()

    def retrieve(self, request, pk=None):
        if request.user and request.user.is_authenticated():
            email = self.get_email_by_pk(request, pk)
            serializer = EmailSerializer(email)
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

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated():
            return Email.objects.filter(
                created_by=self.request.user,
                archived=False,
                is_sent=True,
                delivered=True).order_by('-created')
        raise NotAuthenticated()

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']

            if isinstance(data, list):
                kwargs['many'] = True
        return super(EmailViewSet, self).get_serializer(*args, **kwargs)

    # GET /emails/<id> if id == 'team' (External)
    @list_route(methods=['get'], url_path='team',
                permission_classes=[IsAdminOrIsSelf])
    def team(self, request):
        if self.request.user and self.request.user.is_authenticated():
            user_profile = UserProfile.objects.get(user=request.user)
            emails = Email.objects.filter(
                team=user_profile.team, archived=False
            ).filter(~Q(created_by=self.request.user))

            page = self.paginate_queryset(emails)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(emails, many=True)
            return BulkResponse(serializer.data, {},
                                len(serializer.data), len(serializer.data))
        raise NotAuthenticated()

    # GET /emails/<id> if id == 'scheduled' (External)
    @list_route(methods=['get'], url_path='scheduled',
                permission_classes=[IsAdminOrIsSelf])
    def scheduled(self, request):
        if self.request.user and self.request.user.is_authenticated():
            now = datetime.datetime.today()
            emails = Email.objects.filter(created_by=request.user,
                                          cancel=False, is_sent=True,
                                          send_at__gte=now
                                          ).order_by('-created')

            page = self.paginate_queryset(emails)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(emails, many=True)
            return BulkResponse(serializer.data, {},
                                len(serializer.data), len(serializer.data))
        raise NotAuthenticated()

    # GET /emails/<id> if id == 'archived' (External)
    @list_route(methods=['get'], url_path='archived',
                permission_classes=[IsAdminOrIsSelf])
    def archived(self, request):
        if self.request.user and self.request.user.is_authenticated():
            emails = Email.objects.filter(
                created_by=request.user, archived=False,
                cancel=False).order_by('-created')

            page = self.paginate_queryset(emails)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(emails, many=True)
            return BulkResponse(serializer.data, {},
                                len(serializer.data), len(serializer.data))
        raise NotAuthenticated()

    # GET /emails/<id> if id == 'cancelscheduled' (External)
    @list_route(methods=['get'], url_path='cancelscheduled',
                permission_classes=[IsAdminOrIsSelf])
    def cancel_scheduled(self, request):
        if self.request.user and self.request.user.is_authenticated():
            now = datetime.datetime.today()
            emails = Email.objects.filter(
                created_by=request.user,
                cancel=False,
                is_sent=True,
                delivered=False,
                send_at__gte=now
            ).order_by('-created')
            # We just have to cancel each emails
            for email in emails:
                email.cancel = True
                email.save()

            serializer = EmailSerializer(emails, many=True)
            return BulkResponse(serializer.data, {},
                                len(serializer.data), len(serializer.data))
        raise NotAuthenticated()

    # GET /emails/<id> if id == 'sent' (External)
    @list_route(methods=['get'], url_path='sent',
                permission_classes=[IsAdminOrIsSelf])
    def sent(self, request):
        if self.request.user and self.request.user.is_authenticated():
            user_profile = UserProfile.objects.get(user=request.user)
            emails = Email.objects.filter(created_by=request.user,
                                          archived=False,
                                          is_sent=True,
                                          cancel=False,
                                          delivered=True).order_by('-created')

            page = self.paginate_queryset(emails)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(emails, many=True)
            return BulkResponse(serializer.data, {},
                                len(serializer.data), len(serializer.data))
        raise NotAuthenticated()

    # GET /emails/<id> if id == 'stats' (External)
    @list_route(methods=['get'], url_path='stats',
                permission_classes=[IsAdminOrIsSelf])
    def stats(self, request):
        return

    # GET /emails/<id> if id == 'campaigns' (External)
    @list_route(methods=['get'], url_path='campaigns',
                permission_classes=[IsAdminOrIsSelf])
    def campaigns(self, request):
        if request.user and request.user.is_authenticated():
            campaigns = Campaign.objects.filter(
                created_by=request.user,
            ).order_by('-created')

            serializer = CampaignSerializer(campaigns, many=True)
            return Response(serializer.data, {})
        raise NotAuthenticated()

    # GET /emails/<id> if id == 'limits' (External)
    @list_route(methods=['get'], url_path='limits',
                permission_classes=[IsAdminOrIsSelf])
    def limits(self, request):
        if request.user and request.user.is_authenticated():
            # Use email model manager
            emails = Email.objects.emails_by_user_today(request.user)

            print emails

            # Setup emails
            sendgrid = 0
            outlook = 0
            gmail = 0
            smtp = 0

            # Loop through emails
            for email in emails:
                if email.method == 'sendgrid':
                    sendgrid += 1
                elif email.method == 'outlook':
                    outlook += 1
                elif email.method == 'gmail':
                    gmail += 1
                elif email.method == 'smtp':
                    smtp += 1

            data = {
                'sendgrid': sendgrid,
                'sendgridLimits': 2500,
                'outlook': outlook,
                'outlookLimits': 500,
                'gmail': gmail,
                'gmailLimits': 500,
                'smtp': smtp,
                'smtpLimits': 2000
            }

            return Response(data, {})
        raise NotAuthenticated()

    # POST /emails/<id> if id == 'upload' (External)
    @list_route(methods=['post'], url_path='upload',
                permission_classes=[IsAdminOrIsSelf],
                parser_classes=(FormParser, MultiPartParser,))
    def upload(self, request):
        if 'file' in request.FILES:
            image_file = request.FILES.get('file')
            random_number = binascii.b2a_hex(os.urandom(15))

            original_file_name = image_file._name
            file_name = image_file._name.replace(' ', '')
            generated_file_name = ''.join(
                [str(request.user.pk), random_number, file_name])
            image_file._name = generated_file_name

            file = EmailImage(file=image_file)
            file.original_name = original_file_name
            file.file_name = generated_file_name
            file.created_by = request.user
            file.save()

            serializer = EmailImageSerializer(file)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /emails/<id> if id == 'bulksend' (External)
    @list_route(methods=['post'], url_path='bulksend',
                permission_classes=[IsAdminOrIsSelf])
    def bulk_send(self, request):
        if 'emailids' in request.data:
            emails = []
            for email_id in request.data['emailids']:
                try:
                    email = self.get_email_by_pk(request, email_id)
                    if not email.is_sent:
                        emails.append(email)
                except Email.DoesNotExist:
                    continue

            self._send_emails(emails)
            serializer = EmailSerializer(emails, many=True)
            return BulkResponse(serializer.data, {},
                                len(serializer.data), len(serializer.data))
        raise ParseError()

    # POST /emails/<id> if id == 'bulkattach' (External)
    @list_route(methods=['post'], url_path='bulkattach',
                permission_classes=[IsAdminOrIsSelf],
                parser_classes=(FormParser, MultiPartParser,))
    def bulk_attach(self, request):
        if 'file' in request.FILES:
            files = self._file_to_file_object(request)

            serializer = FileSerializer(files, many=True)
            return Response(serializer.data, {})
        raise ParseError()

    # GET /emails/<id>/send (External)
    @detail_route(methods=['get'], url_path='send',
                  permission_classes=[IsAdminOrIsSelf])
    def send(self, request, pk=None):
        email = self.get_email_by_pk(request, pk)
        if not email.is_sent:
            self._send_emails([email])

        serializer = EmailSerializer(email)
        return Response(serializer.data, {})

    # GET /emails/<id>/cancel (External)
    @detail_route(methods=['get'], url_path='cancel',
                  permission_classes=[IsAdminOrIsSelf])
    def cancel(self, request, pk=None):
        email = self.get_email_by_pk(request, pk)
        email.cancel = True
        email.save()

        serializer = EmailSerializer(email)
        return Response(serializer.data, {})

    # GET /emails/<id>/archive (External)
    @detail_route(methods=['get'], url_path='archive',
                  permission_classes=[IsAdminOrIsSelf])
    def archive(self, request, pk=None):
        email = self.get_email_by_pk(request, pk)
        email.archived = True
        email.save()

        serializer = EmailSerializer(email)
        return Response(serializer.data, {})

    # GET /emails/<id>/logs (External)
    @detail_route(methods=['get'], url_path='logs',
                  permission_classes=[IsAdminOrIsSelf])
    def logs(self, request, pk=None):
        return

    # GET /emails/<id>/add-attachments (External)
    @detail_route(methods=['post'], url_path='add-attachments',
                  permission_classes=[IsAdminOrIsSelf])
    def add_attachments(self, request, pk=None):
        if 'attachments' in request.data:
            email = self.get_email_by_pk(request, pk)
            for attachment in request.data['attachments']:
                # Add that attachment to the email
                file = File.objects.get(pk=attachment)
                email.attachments.set(file)
                email.save()

            serializer = EmailSerializer(email)
            return Response(serializer.data, {})
        raise ParseError()

    # POST /emails/<id>/attach (External)
    @detail_route(methods=['post'], url_path='attach',
                  permission_classes=[IsAdminOrIsSelf],
                  parser_classes=(FormParser, MultiPartParser,))
    def attach(self, request, pk=None):
        email = self.get_email_by_pk(request, pk)
        if 'file' in request.FILES:
            files = self._file_to_file_object(request)

            for file in files:
                email.attachments.add(file)
                email.save()

            serializer = EmailSerializer(email)
            return Response(serializer.data, {})
        raise ParseError()
