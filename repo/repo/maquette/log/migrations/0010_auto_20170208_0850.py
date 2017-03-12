# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-08 13:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log', '0009_auto_20170208_0839'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='yelp_website',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
