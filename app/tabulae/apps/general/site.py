# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.sites.shortcuts import get_current_site


def generate_site_url(request):
    site_url = get_current_site(request)
    if 'localhost' in site_url.domain:
        return 'http://' + site_url.domain
    else:
        return 'https://api.newsai.org'


def generate_url_outlook(request):
    site_url = generate_site_url(request)
    ending = '/api/auth/complete/outlook-oauth2/'
    return site_url + ending


def generate_url_gmail(request):
    site_url = generate_site_url(request)
    ending = '/api/auth/complete/gmail-oauth2/'
    return site_url + ending


def generate_url_nylas(request):
    site_url = generate_site_url(request)
    ending = '/api/auth/complete/nylas-oauth/'
    return site_url + ending


def product_site_url(request):
    product_site = 'https://tabulae.newsai.co'
    return product_site
