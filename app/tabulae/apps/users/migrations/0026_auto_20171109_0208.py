# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-09 02:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_userprofile_outlook_email_provider'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name_plural': 'user-profiles'},
        ),
    ]
