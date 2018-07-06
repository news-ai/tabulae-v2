# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-25 01:51
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_auto_20171025_0151'),
        ('contacts', '0004_auto_20171020_1748'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contact',
            options={'verbose_name_plural': 'contacts'},
        ),
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together=set([('team', 'email')]),
        ),
    ]
