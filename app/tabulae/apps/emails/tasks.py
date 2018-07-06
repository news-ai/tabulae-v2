# -*- coding: utf-8 -*-
# Stdlib imports
from __future__ import absolute_import

# Third-party app imports
from sendgrid.helpers.mail import *
from celery import shared_task

# Imports from app
from tabulae.apps.emails.models import Email


@shared_task
def send_sendgrid(email_id):
    email = Email.objects.get(pk=email_id)

    if not email.delivered:
        response = email.send_sendgrid_email()

        if response._status_code == 202:
            email.save()
            return True
        else:
            raise Exception(response)


@shared_task
def send_gmail(email_id):
    email = Email.objects.get(pk=email_id)

    if not email.delivered:
        response = email.send_gmail_email()

        if response:
            email.save()
            return True
    return False


@shared_task
def send_outlook(email_id):
    email = Email.objects.get(pk=email_id)

    if not email.delivered:
        response = email.send_outlook_email()

        if response:
            email.save()
            return True
    return False


@shared_task
def send_smtp(email_id):
    email = Email.objects.get(pk=email_id)

    if not email.delivered:
        response = email.send_external_email()

        if response:
            email.save()
            return True
    return False
