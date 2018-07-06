# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-13 00:55
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0001_initial'),
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0007_auto_20171012_2353'),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomFieldsMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.TextField(default=b'')),
                ('value', models.TextField(default=b'')),
                ('custom_field', models.BooleanField(default=False)),
                ('hidden', models.BooleanField(default=False)),
                ('created_by', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MediaList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.TextField(default=b'')),
                ('client_name', models.TextField(default=b'')),
                ('custom_fields', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
                ('fields', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
                ('public_list', models.BooleanField(default=False)),
                ('archived', models.BooleanField(default=False)),
                ('subscribed', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('client', models.ManyToManyField(related_name='_medialist_client_+', to='users.Client')),
                ('contacts', models.ManyToManyField(related_name='_medialist_contacts_+', to='contacts.Contact')),
                ('created_by', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('fields_map', models.ManyToManyField(related_name='_medialist_fields_map_+', to='lists.CustomFieldsMap')),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='files.File')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
