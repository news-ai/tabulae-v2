# -*- coding: utf-8 -*-
# Core Django imports
from django.contrib.auth import get_user_model

# Third-party app imports
from rest_framework.serializers import ModelSerializer

# Imports from app
from tabulae.apps.general.response import form_response
from tabulae.apps.general.serializers import DynamicFieldsModelSerializer
from tabulae.apps.users.models import UserProfile
from .models import Template


class TemplateSerializer(ModelSerializer):

    def to_representation(self, obj):
        has_data = False
        included = {}
        if isinstance(obj, dict):
            if 'data' in obj and 'included' in obj:
                has_data = True
                included = obj['included']

                obj = obj['data']

        template = {
            'id': obj.pk,
            'type': 'templates',
            'createdby': obj.created_by and obj.created_by.pk,
            'created': obj.created,
            'updated': obj.updated,

            'name': obj.name,
            'subject': obj.subject,
            'body': obj.body,
            'archived': obj.archived
        }

        if has_data:
            return {
                'data': template,
                'included': included,
            }

        return template

    def create(self, data):
        template = Template.objects.create(**data)

        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

        user_profile = UserProfile.objects.get(user=user)
        template.team = user_profile.team

        template.created_by = user
        template.save()

        return template

    def update(self, template, validated_data):
        template.name = validated_data.get(
            'name', template.name)
        template.subject = validated_data.get(
            'subject', template.subject)

        template.body = validated_data.get(
            'body', template.body)
        template.archived = validated_data.get(
            'archived', template.archived)

        template.save()

        return form_response(template, {})

    class Meta:
        model = Template
        fields = ('name', 'subject', 'body', 'archived',)
