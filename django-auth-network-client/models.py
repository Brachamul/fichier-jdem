import os, requests, json
import uuid
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User



class NetworkUser(models.Model):

	''' The NetworkUser is an extension of the standard Django User model.
	Each User is '''

	user = models.OneToOneField(User, null=True, related_name='network_user')
	uuid = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)

	# TODO : handle cascading when a user is deleted on Centrifuge

	def __str__(self):
		return str(self.user)

	def update_user_details(self):

		''' This will either generate or update a NetworkUser
		based on the user's data on the auth_network '''

		print('==========')
		print('updating or creating user')
		
		# Request the user's details from the auth_network
		# TODO : catch request errors
		request_user_details = requests.get(
			'{AUTH_NETWORK_URL}get-details/{AUTH_NETWORK_KEY}/{AUTH_NETWORK_SECRET}/{user_uuid}'.format(
				AUTH_NETWORK_URL = settings.AUTH_NETWORK_URL,
				AUTH_NETWORK_KEY = settings.AUTH_NETWORK_KEY,
				AUTH_NETWORK_SECRET = settings.AUTH_NETWORK_SECRET,
				user_uuid = self.uuid,
				)
			)

		# The user_details_request returns a Response object. Its '.text' is JSON.
		user_details = json.loads(request_user_details.text)

		print('==========')
		print(str(user_details))

		# If this is the first time the user is authenticating to this client app
		# We'll need to create an account for them
		if not self.user :
			self.user = User.objects.create_user(user_details['username'])
			self.save()

		# Now, update the user's account with details from the auth_network
		User.objects.filter(pk=self.user.pk).update(**user_details)
		self.user.save()
