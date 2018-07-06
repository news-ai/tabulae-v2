# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-20 17:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('templates', '0002_auto_20171013_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
