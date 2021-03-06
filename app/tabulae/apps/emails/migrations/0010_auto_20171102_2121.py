# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-02 21:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('emails', '0009_auto_20171027_0040'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('subject', models.TextField(blank=True, default=b'')),
                ('delivered', models.IntegerField(blank=True, default=0)),
                ('opens', models.IntegerField(blank=True, default=0)),
                ('unique_opens', models.IntegerField(blank=True, default=0)),
                ('clicks', models.IntegerField(blank=True, default=0)),
                ('unique_clicks', models.IntegerField(blank=True, default=0)),
                ('bounces', models.IntegerField(blank=True, default=0)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='email',
            name='campaign',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='emails.Campaign'),
        ),
    ]
