# -*- coding: utf-8 -*-
import base64

# Core Django imports
from django.contrib.postgres.fields import ArrayField
from django.db import models

# Third-party app imports
import nylas
from sendgrid.helpers.mail import Mail, Content, Attachment
from sendgrid.helpers.mail import Email as SendGridEmail

# Imports from app
from tabulae.apps.integrations.send_grid import sg
from tabulae.apps.general.models import BaseModel
from tabulae.apps.users.models import UserProfile
from .managers import EmailManager
from tabulae.settings.secrets import (
    NYLAS_OAUTH_CLIENT_ID,
    NYLAS_OAUTH_CLIENT_SECRET
)


class Campaign(BaseModel):
    subject = models.TextField(blank=True, default='')

    delivered = models.IntegerField(blank=True, default=0)

    opens = models.IntegerField(blank=True, default=0)
    unique_opens = models.IntegerField(blank=True, default=0)

    clicks = models.IntegerField(blank=True, default=0)
    unique_clicks = models.IntegerField(blank=True, default=0)

    replies = models.IntegerField(blank=True, default=0)
    unique_replies = models.IntegerField(blank=True, default=0)

    bounces = models.IntegerField(blank=True, default=0)

    class Meta:
        verbose_name_plural = 'campaigns'

    def __unicode__(self):
        return self.created_by.email + ' ' + self.subject


class Email(BaseModel):
    method = models.TextField(blank=True, default='')

    list_in = models.ForeignKey('lists.MediaList', related_name='+', null=True)
    template = models.ForeignKey(
        'templates.Template', related_name='+', null=True)
    contact = models.ForeignKey(
        'contacts.Contact', related_name='+', null=True)
    client = models.ForeignKey('users.Client', related_name='+', null=True)

    from_email = models.EmailField(blank=True, max_length=254)

    sender = models.EmailField(blank=True, max_length=254)
    to = models.EmailField(blank=True, max_length=254)
    subject = models.TextField(blank=True, default='')
    base_subject = models.TextField(blank=True, default='')
    body = models.TextField(blank=True, default='')

    campaign = models.ForeignKey(Campaign, related_name='+', null=True)

    CC = ArrayField(models.CharField(
        max_length=200), blank=True, default=list)
    BCC = ArrayField(models.CharField(
        max_length=200), blank=True, default=list)

    first_name = models.TextField(blank=True, default='')
    last_name = models.TextField(blank=True, default='')

    send_at = models.DateTimeField(editable=True, null=True, blank=True)

    sendgrid_id = models.TextField(blank=True, default='')
    batch_id = models.TextField(blank=True, default='')

    nylas_account_id = models.TextField(blank=True, default='')
    nylas_id = models.TextField(blank=True, default='')
    nylas_thread_id = models.TextField(blank=True, default='')

    team = models.ForeignKey('users.Team', related_name='+', null=True)

    attachments = models.ManyToManyField(
        'files.File', blank=True, related_name='+')

    delivered = models.BooleanField(blank=True, default=False)
    bounced_reasons = models.BooleanField(blank=True, default=False)
    bounced = models.BooleanField(blank=True, default=False)
    clicked = models.IntegerField(blank=True, default=0)
    opened = models.IntegerField(blank=True, default=0)
    spam = models.BooleanField(blank=True, default=False)
    cancel = models.BooleanField(blank=True, default=False)
    dropped = models.BooleanField(blank=True, default=False)
    replies = models.IntegerField(blank=True, default=0)

    sendgrid_opened = models.IntegerField(blank=True, default=0)
    sendgrid_clicked = models.IntegerField(blank=True, default=0)

    archived = models.BooleanField(blank=True, default=False)

    is_sent = models.BooleanField(blank=True, default=False)

    objects = EmailManager()

    class Meta:
        verbose_name_plural = 'emails'

    def __unicode__(self):
        return self.created_by.email + ' ' + self.to + ' ' + self.subject

    def send_sendgrid_email(self):
        self.is_sent = True

        user_full_name = ' '.join(
            [self.created_by.first_name, self.created_by.last_name])
        from_email = SendGridEmail(self.created_by.email, user_full_name)

        subject = self.subject
        content = Content('text/html', self.body)

        contact_full_name = ' '.join([self.first_name, self.last_name])
        to_email = SendGridEmail(self.to, contact_full_name)

        mail = Mail(from_email, subject, to_email, content)

        if len(self.CC) > 0:
            for cc in self.CC:
                mail.personalizations[0].add_cc(SendGridEmail(cc))

        if len(self.BCC) > 0:
            for bcc in self.BCC:
                mail.personalizations[0].add_bcc(SendGridEmail(bcc))

        if self.attachments.count() > 0:
            attachments = self.attachments.all()
            for file_attachment in attachments:
                # Content Type must exist
                if file_attachment.content_type != '':
                    body = file_attachment.file.read()
                    base_64_body = base64.b64encode(body)

                    attachment = Attachment()
                    attachment.content = base_64_body
                    attachment.type = file_attachment.content_type
                    attachment.filename = file_attachment.original_name
                    attachment.disposition = 'attachment'
                    attachment.content_id = file_attachment.original_name
                    mail.add_attachment(attachment)

        body = mail.get()
        response = sg.client.mail.send.post(request_body=body)

        if response._headers and 'X-Message-Id' in response._headers:
            sendgrid_id = response._headers['X-Message-Id']
            self.method = 'sendgrid'
            self.delivered = True
            self.sendgrid_id = sendgrid_id

        return response

    def send_nylas_email(self, token):
        self.is_sent = True

        client = nylas.APIClient(NYLAS_OAUTH_CLIENT_ID,
                                 NYLAS_OAUTH_CLIENT_SECRET, token)

        all_attachments = []
        if self.attachments.count() > 0:
            attachments = self.attachments.all()
            for file_attachment in attachments:
                if file_attachment.content_type != '':
                    body = file_attachment.file.read()
                    base_64_body = base64.b64encode(body)

                    # Create the attachment
                    myfile = client.files.create()
                    myfile.filename = file_attachment.original_name
                    myfile.data = base_64_body

                    all_attachments.append(myfile)

        contact_full_name = ' '.join([self.first_name, self.last_name])

        draft = client.drafts.create()
        draft.to = [{
            'name': contact_full_name,
            'email': self.to
        }]
        draft.subject = self.subject
        draft.body = self.body
        draft.tracking = {
            'links': 'true',
            'opens': 'true',
            'thread_replies': 'true',
            'payload': str(self.pk)
        }

        for attachment in all_attachments:
            draft.attach(attachment)

        try:
            resp = draft.send()
            self.delivered = True
            self.nylas_account_id = resp['account_id']
            self.nylas_id = resp['id']
            self.nylas_thread_id = resp['thread_id']
            return resp
        except nylas.client.errors.ConnectionError as e:
            print('Unable to connect to the SMTP server.')
            raise Exception(e)
        except nylas.client.errors.MessageRejectedError as e:
            print('Message got rejected by the SMTP server!')
            print(e.message)
            print(e.server_error)
            raise Exception(e)

    def send_gmail_email(self):
        user_profile = UserProfile.objects.get(user=self.created_by)
        return self.send_nylas_email(
            user_profile.gmail_nylas_access_token)

    def send_outlook_email(self):
        user_profile = UserProfile.objects.get(user=self.created_by)
        return self.send_nylas_email(
            user_profile.outlook_access_token)

    def send_external_email(self):
        user_profile = UserProfile.objects.get(user=self.created_by)
        return self.send_nylas_email(
            user_profile.external_email_access_token)
