# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-09 02:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_auto_20171109_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='gmaiL_nylas_code',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
