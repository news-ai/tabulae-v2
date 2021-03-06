# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-06 23:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_userprofile_gmail_nylas_access_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='outlook_access_token',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='outlook_expires_in',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='outlook_microsoft_code',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='outlook_refresh_token',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='outlook_token_type',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
