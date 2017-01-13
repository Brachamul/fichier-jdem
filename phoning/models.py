# -*- coding: utf-8 -*-
import os
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta
from fichiers_adherents.models import Adherent


class Operation(models.Model):
	name = models.CharField(max_length=255)
	query = models.CharField(max_length=5000, help_text="eg: { 'federation': 64, }")
	authorized_users = models.ManyToManyField(User, related_name='allowed_operations', blank=True)
	max_requests = models.SmallIntegerField(default=10) # per 20 minutes
	targets_called_successfully = models.ManyToManyField(Adherent, related_name='operations_where_called', blank=True)
	targets_with_wrong_number = models.ManyToManyField(Adherent, related_name='operations_where_wrong_number_found', blank=True)
	valid_until = models.DateTimeField()
	created_by = models.ForeignKey(User)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

class UserRequest(models.Model):
	user = models.ForeignKey(User)
	operation = models.ForeignKey(Operation)
	date = models.DateTimeField(auto_now_add=True)
