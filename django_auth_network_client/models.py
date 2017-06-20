import os, requests, json, uuid, textwrap
from django.conf import settings
from django.db import models, IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, send_mass_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User




class UserCreationError(Exception): pass



class NetworkUser(models.Model):

	''' The NetworkUser is an extension of the standard Django User model. '''

	user = models.OneToOneField(User, null=True, related_name='network_user')
	uuid = models.UUIDField(primary_key=True, max_length=32, default=uuid.uuid4, editable=False)

	def __str__(self):
		return str(self.user)

	def update_user_details(self, user_details):

		''' This will either generate or update a NetworkUser
		based on the data sent by the auth_network '''

		if not self.user :
			# If the user doesn't already exist in this client app,
			# we'll need to create an account for them
			
			# check if a user with that username doesn't already exist
			users_with_same_username = User.objects.filter(username=user_details['username'])
			if not users_with_same_username :
				# no user with that username exist, let's try and create the user
				try :
					self.user = User.objects.create_user(**user_details)
				except IntegrityError :
					raise UserCreationError
				else :
					warn_when_new_account(user_details['username']) # sends an email to the admins

			else :
				# there is already a user with that username, so we want to bind the network user to it
				# this is a recovery feature, not supposed to actually be used

				NetworkUser.objects.filter(user=users_with_same_username[0]).delete()
				# clear networkusers that might already be bound to that user

				self.user = users_with_same_username[0]


			self.save()

		else :
			# Otherwise, just update the user's account with more recent details
			user = User.objects.filter(pk=self.user.pk) #
			user.update(**user_details)


def warn_when_new_account(username):
	subject = '[Fiji] ' + '{} a créé un compte !'.format(username)
	text = \
		'''

		{} vient de créer un compte sur http://fichier.jdem.fr.
		Si nécessaire, vous pouvez désormais lui accorder des droits sur une partie du fichier.
		
		-
		Message automatique envoyé par Fiji
		
		'''.format(username)
	from_email = settings.EMAIL_FROM
	text = textwrap.dedent(text) # removes useless indentations from the email text
	recipient_list = ['federations@jeunes-democrates.org',]
	send_mail(subject, text, from_email, recipient_list)