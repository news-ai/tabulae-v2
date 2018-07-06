# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-12 23:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_client_invite'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invite',
            options={'verbose_name_plural': 'invites'},
        ),
        migrations.AddField(
            model_name='invite',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
    ]
