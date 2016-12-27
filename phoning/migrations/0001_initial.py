# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-26 12:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fichiers_adherents', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Operation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('query', models.CharField(max_length=5000)),
                ('max_requests', models.SmallIntegerField(default=10)),
                ('valid_until', models.DateTimeField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('authorized_users', models.ManyToManyField(blank=True, related_name='allowed_operations', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('targets_called_successfully', models.ManyToManyField(blank=True, related_name='operations_where_called', to='fichiers_adherents.Adherent')),
                ('targets_with_wrong_number', models.ManyToManyField(blank=True, related_name='operations_where_wrong_number_found', to='fichiers_adherents.Adherent')),
            ],
        ),
        migrations.CreateModel(
            name='UserRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('operation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='phoning.Operation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
