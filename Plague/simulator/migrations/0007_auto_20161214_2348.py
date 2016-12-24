# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-12-15 04:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('simulator', '0006_auto_20161214_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airline',
            name='from_airport',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='from_airport', to='simulator.Airport'),
        ),
        migrations.AlterField(
            model_name='airline',
            name='to_airport',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='to_airport', to='simulator.Airport'),
        ),
    ]