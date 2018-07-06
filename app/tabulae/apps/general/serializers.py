# -*- coding: utf-8 -*-
# Third-party app imports
from rest_framework.serializers import ModelSerializer

# Imports from app
from .response import form_bulk_response


class DynamicFieldsModelSerializer(ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            self.allowed = allowed

# Source:
# http://stackoverflow.com/questions/23643204/django-rest-framework-dynamically-return-subset-of-fields
