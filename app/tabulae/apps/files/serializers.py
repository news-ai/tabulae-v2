# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model

# Third-party app imports
from rest_framework.serializers import ModelSerializer

# Imports from app
from .models import File, EmailImage


class FileSerializer(ModelSerializer):

    def to_representation(self, obj):
        has_data = False
        included = {}
        if isinstance(obj, dict):
            if 'data' in obj and 'included' in obj:
                has_data = True
                included = obj['included']

                obj = obj['data']

        file = {
            'id': obj.pk,
            'type': 'lists',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'originalname': obj.original_name,
            'filename': obj.file_name,
            'url': obj.url,
            'headernames': obj.header_names,
            'order': obj.order,
            'imported': obj.imported,
            'fileexists': obj.file_exists,
            'contenttype': obj.content_type
        }

        if has_data:
            return {
                'data': file,
                'included': included,
            }

        return file

    class Meta:
        model = File
        fields = ('original_name', 'file_name',
                  'url',  'file', 'header_names', 'order',
                  'imported', 'file_exists',)


class EmailImageSerializer(ModelSerializer):

    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'type': 'email-images',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'originalname': obj.original_name,
            'filename': obj.file_name,
            'url': obj.file and obj.file.url,
        }

    class Meta:
        model = EmailImage
