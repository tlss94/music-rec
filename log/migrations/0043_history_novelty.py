# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-26 14:01
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields
import log.models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0042_auto_20170425_1429'),
    ]

    operations = [
        migrations.AddField(
            model_name='history',
            name='novelty',
            field=jsonfield.fields.JSONField(default=log.models.default_songs),
        ),
    ]