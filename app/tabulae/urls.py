# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework_jwt.views import (
    refresh_jwt_token,
    verify_jwt_token,
    obtain_jwt_token,
)
from rest_framework_swagger.views import get_swagger_view
from registration.forms import RegistrationFormUniqueEmail
from registration.signals import user_registered

# Core Django imports
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

# Imports from app
from tabulae.apps.api_router_v1 import router
from tabulae.apps.integrations.gmail import GmailLoginView, GmailCompleteView
from tabulae.apps.integrations.outlook import (
    OutlookLoginView,
    OutlookCompleteView,
)
from tabulae.apps.incomings.nylas import NylasMessageIncomingView
from tabulae.apps.integrations.smtp import NylasLoginView, NylasCompleteView
from tabulae.apps.users.forms import MyCustomUserForm
from tabulae.apps.users.views import RegistrationView
from tabulae.apps.users.utils import create_user_profile

# Initialize signals
user_registered.connect(create_user_profile)

schema_view = get_swagger_view(title='NewsAI API')

# Initialize pattners for API
urlpatterns = [
    # Admin platform
    url(r'^admin/', include(admin.site.urls)),

    # Docs
    url(r'^docs/$', schema_view),

    # API & JSON Web Tokens
    url(r'^api/v1/', include(router.urls, namespace='v1')),

    # Payments
    url(r'^api/payments/', include('djstripe.urls', namespace='djstripe')),

    # Authentication
    url(r'^api/auth/register/$',
        RegistrationView.as_view(form_class=MyCustomUserForm)),
    url(r'^api/auth/', include('registration.backends.hmac.urls')),

    url(r'^api/auth/login/gmail-oauth2/',
        GmailLoginView, name='login-gmail-oauth2'),
    url(r'^api/auth/complete/gmail-oauth2/',
        GmailCompleteView, name='complete-gmail-oauth2'),

    url(r'^api/auth/login/outlook-oauth2/',
        OutlookLoginView, name='login-outlook-oauth2'),
    url(r'^api/auth/complete/outlook-oauth2/',
        OutlookCompleteView, name='complete-outlook-oauth2'),

    url(r'^api/auth/login/nylas-oauth/',
        NylasLoginView, name='login-nylas-oauth'),
    url(r'^api/auth/complete/nylas-oauth/',
        NylasCompleteView, name='complete-nylas-oauth'),

    # Incoming
    url(r'^api/v1/incoming/nylas-message/',
        NylasMessageIncomingView, name='v1-incoming-nylas-message'),

    # Django authentication for everything else
    url(r'^api/auth/', include('social_django.urls', namespace='social')),
]
