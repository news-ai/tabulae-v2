# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-08 23:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_auto_20171106_2324'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='external_email_access_token',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='external_email_account_id',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='external_email_provider',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='external_email_token_type',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='external_email_username',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
