# -*- coding: utf-8 -*-
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import os
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class UserRequest(models.Model):
	user = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)