# -*- coding: utf-8 -*-
# Third-party app imports
import sendgrid

# Imports from app
from tabulae.settings.secrets import NEWSAI_SENDGRID_API_KEY

sg = sendgrid.SendGridAPIClient(apikey=NEWSAI_SENDGRID_API_KEY)
