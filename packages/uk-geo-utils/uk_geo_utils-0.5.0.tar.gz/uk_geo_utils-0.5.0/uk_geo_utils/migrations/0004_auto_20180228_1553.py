# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-28 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uk_geo_utils', '0003_auto_20171030_1504'),
    ]

    operations = [
        migrations.RenameField(
            model_name='onspd',
            old_name='hro',
            new_name='nhser',
        ),
        migrations.RenameField(
            model_name='onspd',
            old_name='gor',
            new_name='rgn',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='cened',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='edind',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='lea',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='oldha',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='oldpct',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='oshaprev',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='psed',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='streg',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='ward98',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='wardc91',
        ),
        migrations.RemoveField(
            model_name='onspd',
            name='wardo91',
        ),
        migrations.AddField(
            model_name='onspd',
            name='ced',
            field=models.CharField(blank=True, max_length=9),
        ),
    ]
