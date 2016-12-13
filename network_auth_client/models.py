import os
import uuid
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User

# http://stackoverflow.com/questions/35528074/django-is-extending-abstractbaseuser-required-to-use-email-as-username-field

class NetworkUser(models.Model):
	user = models.ForeignKey(User)
	uuid = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)

	def __str__(self):
		return str(self.user)