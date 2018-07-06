# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-25 01:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20171024_0127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='blog',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='client',
            name='instagram',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='client',
            name='linkedin',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='client',
            name='name',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='client',
            name='notes',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='client',
            name='twitter',
            field=models.TextField(blank=True, default=b''),
        ),
        migrations.AlterField(
            model_name='client',
            name='url',
            field=models.URLField(blank=True, default=b''),
        ),
    ]
