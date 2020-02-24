# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-24 18:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0019_auto_20191028_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='facility',
            name='nhif_accreditation',
            field=models.NullBooleanField(default=False, help_text=b'A flag to indicate whether facility is accredited by nhif'),
        ),
        migrations.AddField(
            model_name='facility',
            name='number_of_emergency_casualty_beds',
            field=models.PositiveIntegerField(default=0, help_text=b'The number of emergency casualty beds  that a facility has e.g 0'),
        ),
        migrations.AddField(
            model_name='facility',
            name='number_of_general_theatres',
            field=models.PositiveIntegerField(default=0, help_text=b'The number of general theatres  that a facility has e.g 0'),
        ),
        migrations.AddField(
            model_name='facility',
            name='number_of_hdu_beds',
            field=models.PositiveIntegerField(default=0, help_text=b'The number of High Dependency Units (HDU) beds that a facility has e.g 0'),
        ),
        migrations.AddField(
            model_name='facility',
            name='number_of_icu_beds',
            field=models.PositiveIntegerField(default=0, help_text=b'The number of Intensive Care Units (ICU) beds that a facility has e.g 0'),
        ),
        migrations.AddField(
            model_name='facility',
            name='number_of_maternity_theatres',
            field=models.PositiveIntegerField(default=0, help_text=b'The number of maternity theatres  that a facility has e.g 0'),
        ),
        migrations.AlterField(
            model_name='facility',
            name='number_of_beds',
            field=models.PositiveIntegerField(default=0, help_text=b'The number of authorized inpatient beds that a facility has. e.g 0'),
        ),
        migrations.AlterField(
            model_name='facility',
            name='number_of_cots',
            field=models.PositiveIntegerField(default=0, help_text=b'The number of authorized cots that a facility has e.g 0'),
        ),
    ]
