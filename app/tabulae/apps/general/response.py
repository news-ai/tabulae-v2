# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework.response import Response as django_response


def form_response(data, included):
    return {
        'data': data,
        'included': included
    }


def form_bulk_response(data, included, count, total):
    return {
        'count': count,
        'data': data,
        'included': included,
        'paging': {
            'cursors': {
                'before': '',
                'after': ''
            },
            'next': ''
        },
        'summary': {
            'total': total
        }
    }


def Response(data, included):
    return django_response(form_response(data, included))


def BulkResponse(data, included, count, total, status=None, headers=None):
    return django_response(form_bulk_response(data, included, count, total),
                           status=status,
                           headers=headers)
