# Taken from
# https://github.com/django-json-api/django-rest-framework-json-api/blob/develop/rest_framework_json_api/utils.py
# and
# https://github.com/django-json-api/django-rest-framework-json-api/blob/develop/rest_framework_json_api/exceptions.py

# -*- coding: utf-8 -*-
# Stdlib imports
import inspect

# Core Django imports
import django.conf
from django.utils import six, encoding

# Third-party app imports
import inflection
from rest_framework import exceptions

# Imports from app
from .errors import detail_to_title


def format_value(value, format_type=None):
    if format_type is None:
        format_type = getattr(django.conf.settings, 'TABULAE_FORMAT_KEYS', False)
    if format_type == 'dasherize':
        # inflection can't dasherize camelCase
        value = inflection.underscore(value)
        value = inflection.dasherize(value)
    elif format_type == 'camelize':
        value = inflection.camelize(value, False)
    elif format_type == 'capitalize':
        value = inflection.camelize(value)
    elif format_type == 'underscore':
        value = inflection.underscore(value)
    return value


def format_error(detail, status):
    return {
        'detail': detail,
        'status': encoding.force_text(status),
        'title': detail_to_title[str(status)] if str(status) in detail_to_title else '',
        'source': {
            'pointer': '/api'
        }
    }


def format_errors(response, context, exc):
    errors = []
    # handle generic errors. ValidationError('test') in a view for example
    if isinstance(response.data, list):
        for message in response.data:
            errors.append(format_error(message, response.status_code))
    # handle all errors thrown from serializers
    else:
        for field, error in response.data.items():
            field = format_value(field)
            # see if they passed a dictionary to ValidationError manually
            if isinstance(error, dict):
                errors.append(error)
            elif isinstance(error, six.string_types):
                classes = inspect.getmembers(exceptions, inspect.isclass)
                errors.append(format_error(error, response.status_code))
            elif isinstance(error, list):
                for message in error:
                    errors.append(format_error(message, response.status_code))
            else:
                errors.append(format_error(error, response.status_code))

    response.data = {
        'errors': errors
    }

    return response


def exception_handler(exc, context):
    from rest_framework.views import exception_handler as context_exception_handler
    response = context_exception_handler(exc, context)

    if not response:
        return response

    return format_errors(response, context, exc)
