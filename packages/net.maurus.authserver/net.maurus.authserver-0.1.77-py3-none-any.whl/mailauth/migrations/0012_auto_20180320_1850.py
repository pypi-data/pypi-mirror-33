# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-20 17:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailauth', '0011_mnserviceuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mngroup',
            name='name',
            field=models.CharField(max_length=255, unique=True, verbose_name='Group name'),
        ),
    ]
