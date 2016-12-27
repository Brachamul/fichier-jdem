import os, requests, json
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

	def update_user_details(self):

		''' This will either generate or update a NetworkUser
		based on the user's data on the auth_network '''

		# Request the user's details from the auth_network
		# TODO : catch request errors
		request_user_details = requests.get(
			'{NETWORK_AUTH_URL}get-details/{NETWORK_AUTH_KEY}/{NETWORK_AUTH_SECRET}/{user_uuid}'.format(
				NETWORK_AUTH_URL = settings.NETWORK_AUTH_URL,
				NETWORK_AUTH_KEY = settings.NETWORK_AUTH_KEY,
				NETWORK_AUTH_SECRET = settings.NETWORK_AUTH_SECRET,
				user_uuid = self.uuid,
				)
			)

		# The user_details_request returns a Response object. Its '.text' is JSON.
		user_details = json.loads(request_user_details.text)
		User.objects.filter(pk=self.user.pk).update(**user_details)
		self.user.save()
