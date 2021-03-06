# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-13 19:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('templates', '0002_auto_20171013_1914'),
        ('emails', '0002_emailsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='template',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='templates.Template'),
        ),
        migrations.AlterField(
            model_name='email',
            name='contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contacts.Contact'),
        ),
        migrations.AlterField(
            model_name='email',
            name='list_in',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='lists.MediaList'),
        ),
        migrations.AlterField(
            model_name='email',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='users.Team'),
        ),
    ]
