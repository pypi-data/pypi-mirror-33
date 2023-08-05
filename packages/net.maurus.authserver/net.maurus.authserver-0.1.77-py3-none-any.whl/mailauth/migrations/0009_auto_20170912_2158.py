# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-12 19:58
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailauth', '0008_auto_20170908_1337'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailinglist',
            name='new_mailfrom',
            field=models.EmailField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='mailinglist',
            name='addresses',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=255), size=None),
        ),
    ]
