# -*- coding: utf-8 -*-
import os
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from datetime import datetime, timedelta



class Operation(models.Model):
	name = models.CharField(max_length=255)
	query = models.CharField(max_length=5000)
	authorized_users = models.ManyToManyField(User, related_name='authorized_users')
	valid_until = models.DateTimeField()
	created_by = models.ForeignKey(User)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

class UserRequest(models.Model):
	user = models.ForeignKey(User)
	operation = models.ForeignKey(Operation)
	date = models.DateTimeField(auto_now_add=True)