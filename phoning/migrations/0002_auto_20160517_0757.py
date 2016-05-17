# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-17 05:57
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('phoning', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoningOperation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=255)),
                ('query', models.CharField(max_length=5000)),
                ('valid_until', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('authorized_users', models.ManyToManyField(related_name='authorized_users', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='userrequest',
            name='operation',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='phoning.PhoningOperation'),
            preserve_default=False,
        ),
    ]
