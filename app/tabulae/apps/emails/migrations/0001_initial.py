# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-10-13 00:55
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0001_initial'),
        ('users', '0007_auto_20171012_2353'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lists', '__first__'),
        ('files', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('method', models.TextField(default=b'')),
                ('from_email', models.EmailField(max_length=254)),
                ('sender', models.EmailField(max_length=254)),
                ('to', models.EmailField(max_length=254)),
                ('subject', models.TextField(default=b'')),
                ('base_subject', models.TextField(default=b'')),
                ('body', models.TextField(default=b'')),
                ('CC', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
                ('BCC', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, default=list, size=None)),
                ('first_name', models.TextField(default=b'')),
                ('last_name', models.TextField(default=b'')),
                ('send_at', models.DateTimeField(auto_now=True)),
                ('sendgrid_id', models.TextField(default=b'')),
                ('sparkpost_id', models.TextField(default=b'')),
                ('batch_id', models.TextField(default=b'')),
                ('gmail_id', models.TextField(default=b'')),
                ('gmail_thread_id', models.TextField(default=b'')),
                ('delivered', models.BooleanField(default=False)),
                ('bounced_reasons', models.BooleanField(default=False)),
                ('bounced', models.BooleanField(default=False)),
                ('clicked', models.IntegerField(default=0)),
                ('opened', models.IntegerField(default=0)),
                ('spam', models.BooleanField(default=False)),
                ('cancel', models.BooleanField(default=False)),
                ('dropped', models.BooleanField(default=False)),
                ('sendgrid_opened', models.IntegerField(default=0)),
                ('sendgrid_clicked', models.IntegerField(default=0)),
                ('archived', models.BooleanField(default=False)),
                ('is_sent', models.BooleanField(default=False)),
                ('attachments', models.ManyToManyField(related_name='_email_attachments_+', to='files.File')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Client')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contacts.Contact')),
                ('created_by', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('list_in', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='lists.MediaList')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Team')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
