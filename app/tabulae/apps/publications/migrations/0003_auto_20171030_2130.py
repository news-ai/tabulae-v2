# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-30 21:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0002_auto_20171020_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='blog',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='publication',
            name='instagram',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='publication',
            name='linkedin',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='publication',
            name='name',
            field=models.TextField(blank=True, default=b'', unique=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='twitter',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='publication',
            name='url',
            field=models.URLField(blank=True, default=b'', unique=True),
        ),
    ]
