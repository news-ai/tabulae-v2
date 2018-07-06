# -*- coding: utf-8 -*-
# Stdlib imports
import datetime
import os

# Third-party app imports
import certifi
from elasticsearch import Elasticsearch, helpers

# Imports from app
from tabulae.settings.secrets import ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD

# Elasticsearch setup
es = Elasticsearch(
    ['https://search.newsai.org'],
    http_auth=(ELASTICSEARCH_USER, ELASTICSEARCH_PASSWORD),
    port=443,
    use_ssl=True,
    verify_certs=True,
    ca_certs=certifi.where(),
)


def format_es_response(es_response):
    if 'CreatedAt' in es_response['_source']['data']:
        if 'T' in es_response['_source']['data']['CreatedAt']:
            now = datetime.datetime.strptime(
                es_response['_source']['data']['CreatedAt'],
                '%Y-%m-%dT%H:%M:%S'
            )

            es_response['_source']['data'][
                'CreatedAt'] = int(now.strftime('%s'))
        else:
            now = datetime.datetime.strptime(
                es_response['_source']['data']['CreatedAt'],
                '%Y-%m-%d'
            )

            es_response['_source']['data'][
                'CreatedAt'] = int(now.strftime('%s'))

    for key in es_response['_source']['data']:
        new_key = key.lower()
        es_response['_source']['data'][
            new_key] = es_response['_source']['data'].pop(key)

    return es_response
