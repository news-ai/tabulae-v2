# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-06 19:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_auto_20171103_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='gmail_nylas_access_token',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
