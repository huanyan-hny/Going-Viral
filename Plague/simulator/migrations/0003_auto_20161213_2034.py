# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-12-14 01:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('simulator', '0002_auto_20161121_1702'),
    ]

    operations = [
        migrations.CreateModel(
            name='Airport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city_name', models.CharField(max_length=200)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('population', models.IntegerField()),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.RenameField(
            model_name='disease',
            old_name='susception_rate',
            new_name='susceptible_rate',
        ),
        migrations.RemoveField(
            model_name='airline',
            name='from_area',
        ),
        migrations.RemoveField(
            model_name='airline',
            name='to_area',
        ),
        migrations.DeleteModel(
            name='Area',
        ),
        migrations.AddField(
            model_name='airport',
            name='country',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='country', to='simulator.Country'),
        ),
        migrations.AddField(
            model_name='airline',
            name='from_airport',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='from_airport', to='simulator.Airport'),
        ),
        migrations.AddField(
            model_name='airline',
            name='to_airport',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='to_airport', to='simulator.Airport'),
        ),
    ]