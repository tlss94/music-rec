# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-22 18:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0044_auto_20170504_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='tracks',
            name='MODE',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='tracks',
            name='spotifyID',
            field=models.CharField(default=b'', max_length=250),
        ),
        migrations.AlterField(
            model_name='tracks',
            name='loudness',
            field=models.FloatField(default=0),
        ),
    ]
