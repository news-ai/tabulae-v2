# -*- coding: utf-8 -*-
# Core Django imports
from django.http import HttpResponse
from django.shortcuts import redirect

# Third-party app imports
from requests import get, post
from oauth2client.client import OAuth2WebServerFlow
from rest_framework.exceptions import NotAuthenticated

# Imports from app
from .nylas import gmail_to_access_token as nylas_gmail_to_access_token

from tabulae.apps.general.site import (
    generate_site_url,
    generate_url_gmail,
    product_site_url
)
from tabulae.apps.users.models import UserProfile
from tabulae.settings.secrets import (
    NYLAS_OAUTH_CLIENT_ID,
    NYLAS_OAUTH_CLIENT_SECRET,
    NEWSAI_GOOGLE_OAUTH2_CLIENT_ID,
    NEWSAI_GOOGLE_OAUTH2_CLIENT_SECRET
)

flow = OAuth2WebServerFlow(client_id=NEWSAI_GOOGLE_OAUTH2_CLIENT_ID,
                           client_secret=NEWSAI_GOOGLE_OAUTH2_CLIENT_SECRET,
                           access_type='offline',
                           prompt='consent',
                           scope=(
                               'https://www.googleapis.com/auth/userinfo.profile '
                               'https://www.googleapis.com/auth/userinfo.email '
                               'https://mail.google.com/ '
                               'https://www.google.com/m8/feeds '
                               'https://www.googleapis.com/auth/calendar '
                               'https://www.googleapis.com/auth/gmail.readonly '
                               'https://www.googleapis.com/auth/gmail.compose '
                               'https://www.googleapis.com/auth/gmail.send'),
                           redirect_uri='')


def GmailLoginView(request):
    if request.user and request.user.is_authenticated():
        flow.redirect_uri = generate_url_gmail(request)
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    raise NotAuthenticated()


def GmailCompleteView(request):
    if request.user and request.user.is_authenticated():
        user_profile = UserProfile.objects.get(user=request.user)
        if 'code' in request.GET:
            code = request.GET.get('code')
            credentials = flow.step2_exchange(code)
            access_token = credentials.get_access_token()

            url = 'https://www.googleapis.com/oauth2/v2/userinfo?alt=json&access_token='
            r = get(url + access_token[0])
            if r.status_code == 200:
                resp = r.json()

                user_profile.outlook = False
                user_profile.external_email = False
                user_profile.gmail = True

                user_profile.gmail_username = resp['email']
                user_profile.gmail_token_type = credentials.token_response[
                    'token_type']
                user_profile.gmail_expires_in = credentials.token_expiry
                user_profile.gmail_refresh_token = credentials.refresh_token
                user_profile.gmail_access_token = access_token[0]
                user_profile.gmail_google_code = resp['id']
                user_profile.save()

                # Setup nylas config
                nylas_access_token_json = nylas_gmail_to_access_token(
                    resp, credentials)
                if 'access_token' in nylas_access_token_json:
                    user_profile.gmaiL_nylas_code = nylas_access_token_json[
                        'account_id']
                    user_profile.gmail_nylas_access_token = nylas_access_token_json[
                        'access_token']
                    user_profile.save()

            return redirect(product_site_url(request))
        return redirect(generate_site_url(request))
    raise NotAuthenticated()
