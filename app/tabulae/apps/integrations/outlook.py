# -*- coding: utf-8 -*-
# Core Django imports
from django.shortcuts import redirect

# Third-party app imports
from rest_framework.exceptions import NotAuthenticated

# Imports from app
from .nylas import generate_smtp_nylas_url, get_oauth_token
from tabulae.apps.general.site import (
    generate_site_url,
    generate_url_outlook,
    product_site_url
)
from tabulae.apps.users.models import UserProfile
from tabulae.settings.secrets import (
    NYLAS_OAUTH_CLIENT_ID,
    NYLAS_OAUTH_CLIENT_SECRET
)


def OutlookLoginView(request):
    if request.user and request.user.is_authenticated():
        redirect_uri = generate_url_outlook(request)
        auth_uri = generate_smtp_nylas_url(redirect_uri)
        return redirect(auth_uri)
    raise NotAuthenticated()


def OutlookCompleteView(request):
    if request.user and request.user.is_authenticated():
        user_profile = UserProfile.objects.get(user=request.user)
        if 'code' in request.GET:
            code = request.GET.get('code')
            access_resp = get_oauth_token(code)

            if access_resp.status_code == 200:
                access_token_object = access_resp.json()

                user_profile.outlook = True
                user_profile.external_email = False
                user_profile.gmail = False

                '''
                access_resp:
                {u'access_token': u'NydGZ6oZFsnKLY8bSsrxOX16A6ffB3',
                u'token_type': u'bearer', u'email_address': u'hi@abhi.co',
                u'account_id': u'5k3rl5bw4elb4n3gb2xayo2m8',
                u'provider': u'namecheap'}
                '''

                print access_token_object

                user_profile.outlook_username = access_token_object[
                    'email_address']
                user_profile.outlook_token_type = access_token_object[
                    'token_type']
                user_profile.outlook_access_token = access_token_object[
                    'access_token']
                user_profile.outlook_microsoft_code = access_token_object[
                    'account_id']
                user_profile.outlook_email_provider = access_token_object[
                    'provider']
                user_profile.save()

            return redirect(product_site_url(request))
        return redirect(generate_site_url(request))
    raise NotAuthenticated()
