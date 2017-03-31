# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-31 18:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phoning', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operation',
            name='targets_called_successfully',
            field=models.ManyToManyField(blank=True, related_name='operations_where_called', to='profiles.Member'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='targets_with_wrong_number',
            field=models.ManyToManyField(blank=True, related_name='operations_where_wrong_number_found', to='profiles.Member'),
        ),
    ]
