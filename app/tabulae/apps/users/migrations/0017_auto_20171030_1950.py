# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-30 19:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20171025_0151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='admins',
            field=models.ManyToManyField(blank=True, related_name='_team_admins_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='team',
            name='max_members',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='team',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='_team_members_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
