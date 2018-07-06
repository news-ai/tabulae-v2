# -*- coding: utf-8 -*-
# Third-party app imports
from celery import shared_task

# Imports from app
from tabulae.apps.integrations.full_contact import fc
from tabulae.apps.contacts.models import Contact


@shared_task
def enrich_contact(contact_id):
    contact = Contact.objects.get(pk=contact_id)

    if contact.email != '':
        fc_data = fc.get_fullcontact_from_email(contact.email)
        if fc_data:
            print fc_data
    return True
