# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-13 16:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0009_auto_20171109_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfieldsmap',
            name='order',
            field=models.IntegerField(blank=True, default=50),
        ),
    ]
