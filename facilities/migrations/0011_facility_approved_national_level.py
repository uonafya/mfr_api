# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-08 14:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0010_auto_20190828_2112'),
    ]

    operations = [
        migrations.AddField(
            model_name='facility',
            name='approved_national_level',
            field=models.BooleanField(default=False, help_text=b'Has the facility been approved at the national level'),
        ),
    ]
