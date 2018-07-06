# -*- coding: utf-8 -*-
# Third-party app imports
from requests import post

# Imports from app
from tabulae.settings.secrets import (
    NEWSAI_GOOGLE_OAUTH2_CLIENT_ID,
    NEWSAI_GOOGLE_OAUTH2_CLIENT_SECRET,
    NYLAS_OAUTH_CLIENT_ID,
    NYLAS_OAUTH_CLIENT_SECRET
)


def generate_smtp_nylas_url(redirect_uri):
    client_id = NYLAS_OAUTH_CLIENT_ID
    response_type = 'code'
    scope = 'email'
    login_hint = ''
    redirect_uri = redirect_uri

    return (
        'https://api.nylas.com/oauth/authorize'
        '?client_id=' + client_id +
        '&response_type=' + response_type +
        '&scope=' + scope +
        '&login_hint=' + login_hint +
        '&redirect_uri=' + redirect_uri
    )


def generate_gmail_authorize_data(resp, credentials):
    nylas_authorize_data = {
        'client_id': NYLAS_OAUTH_CLIENT_ID,
        'name': resp['name'],
        'email_address': resp['email'],
        'provider': 'gmail',
        'settings': {
            'google_client_id': NEWSAI_GOOGLE_OAUTH2_CLIENT_ID,
            'google_client_secret': NEWSAI_GOOGLE_OAUTH2_CLIENT_SECRET,
            'google_refresh_token': credentials.refresh_token,
        }
    }

    return nylas_authorize_data


def get_oauth_token(code):
    nylas_authorize_data = {
        'client_id': NYLAS_OAUTH_CLIENT_ID,
        'client_secret': NYLAS_OAUTH_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code
    }

    nylas_authorize_resp = post(
        'https://api.nylas.com/oauth/token',
        json=nylas_authorize_data,
    )

    return nylas_authorize_resp
    


def add_email(nylas_authorize_data):
    nylas_authorize_resp = post(
        'https://api.nylas.com/connect/authorize',
        json=nylas_authorize_data,
    )

    return nylas_authorize_resp


def get_access_token(nylas_authorize_resp):
    nylas_code = nylas_authorize_resp.json()['code']

    nylas_token_data = {
        'client_id': NYLAS_OAUTH_CLIENT_ID,
        'client_secret': NYLAS_OAUTH_CLIENT_SECRET,
        'code': nylas_code,
    }

    nylas_token_resp = post(
        'https://api.nylas.com/connect/token',
        json=nylas_token_data,
    )

    return nylas_token_resp


def gmail_to_access_token(resp, credentials):
    nylas_access_token = ''
    nylas_authorize_data = generate_gmail_authorize_data(resp, credentials)
    nylas_authorize_resp = add_email(nylas_authorize_data)
    if nylas_authorize_resp.status_code == 200:
        nylas_token_resp = get_access_token(
            nylas_authorize_resp)
        nylas_access_token_json = nylas_token_resp.json()
        return nylas_access_token_json
    return {}
