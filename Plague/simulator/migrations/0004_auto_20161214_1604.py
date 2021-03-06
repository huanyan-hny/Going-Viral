# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-12-14 21:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulator', '0003_auto_20161213_2034'),
    ]

    operations = [
        migrations.RenameField(
            model_name='airline',
            old_name='arrival',
            new_name='arrival_time',
        ),
        migrations.RenameField(
            model_name='airline',
            old_name='departure',
            new_name='departure_time',
        ),
        migrations.AlterField(
            model_name='airport',
            name='city_name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='disease',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
