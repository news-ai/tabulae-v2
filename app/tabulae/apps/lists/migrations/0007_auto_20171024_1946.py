# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-24 19:46
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0006_auto_20171024_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medialist',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
