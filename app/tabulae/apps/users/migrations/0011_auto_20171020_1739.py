# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-20 17:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_emailcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailcode',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
