# -*- coding: utf-8 -*-
# Third-party app imports
from fullcontact import FullContact

# Imports from app
from tabulae.settings.secrets import FULLCONTACT_API_KEY

fc = FullContact(FULLCONTACT_API_KEY)


def get_fullcontact_from_email(email):
    r = fc.person(email=email)
    if r.status_code == 200:
        return r.json()
    return None
