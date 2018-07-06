# -*- coding: utf-8 -*-
# Core Django imports
from django.http import HttpResponse
from django.shortcuts import redirect

# Third-party app imports
from requests import get, post
from oauth2client.client import OAuth2WebServerFlow
from rest_framework.exceptions import NotAuthenticated

# Imports from app
from .nylas import generate_smtp_nylas_url, get_oauth_token

from tabulae.apps.general.site import (
    generate_site_url,
    generate_url_nylas,
    product_site_url
)
from tabulae.apps.users.models import UserProfile


def NylasLoginView(request):
    if request.user and request.user.is_authenticated():
        redirect_uri = generate_url_nylas(request)
        auth_uri = generate_smtp_nylas_url(redirect_uri)
        return redirect(auth_uri)
    raise NotAuthenticated()


def NylasCompleteView(request):
    if request.user and request.user.is_authenticated():
        user_profile = UserProfile.objects.get(user=request.user)
        if 'code' in request.GET:
            code = request.GET.get('code')
            access_resp = get_oauth_token(code)

            if access_resp.status_code == 200:
                access_token_object = access_resp.json()

                user_profile.outlook = False
                user_profile.external_email = True
                user_profile.gmail = False

                '''
                access_resp:
                {u'access_token': u'NydGZ6oZFsnKLY8bSsrxOX16A6ffB3',
                u'token_type': u'bearer', u'email_address': u'hi@abhi.co',
                u'account_id': u'5k3rl5bw4elb4n3gb2xayo2m8',
                u'provider': u'namecheap'}
                '''

                user_profile.external_email_username = access_token_object[
                    'email_address']
                user_profile.external_email_token_type = access_token_object[
                    'token_type']
                user_profile.external_email_access_token = access_token_object[
                    'access_token']
                user_profile.external_email_account_id = access_token_object[
                    'account_id']
                user_profile.external_email_provider = access_token_object[
                    'provider']
                user_profile.save()

            return redirect(product_site_url(request))
        return redirect(generate_site_url(request))
    raise NotAuthenticated()
