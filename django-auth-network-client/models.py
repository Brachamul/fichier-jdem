import os, requests, json
import uuid
from django.db import models, IntegrityError
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User



class UserCreationError(Exception): pass

class NetworkUser(models.Model):

	''' The NetworkUser is an extension of the standard Django User model.
	Each User is '''

	user = models.OneToOneField(User, null=True, related_name='network_user')
	uuid = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)

	# TODO : handle cascading when a user is deleted on Centrifuge

	def __str__(self):
		return str(self.user)

	def update_user_details(self, user_details):

		''' This will either generate or update a NetworkUser
		based on the data sent by the auth_network '''

		print('USER DETAILS : ', user_details)

		if not self.user :
			# If the user doesn't already exist in this client app,
			# we'll need to create an account for them
			try :
				self.user = User.objects.create_user(user_details['username'])
			except IntegrityError :
				raise UserCreationError
			self.save()

		# Now, update the user's account with details from the auth_network
		User.objects.filter(pk=self.user.pk).update(**user_details) # 
		self.user.save()
