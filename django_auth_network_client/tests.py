import uuid
from django.test import TestCase, Client

from django.contrib.auth.models import User
from django.core import mail
from django_auth_network_client.models import NetworkUser, warn_when_new_account


class NetworkUserTestCase(TestCase):

	def test__update_user_details__new_user(self):

		network_user, created = NetworkUser.objects.get_or_create(uuid=uuid.uuid4())

		user_details = {
			'username': 'Monsieur Patate',
			'email': 'monsieur.patate@gmail.com',
			'first_name': 'Monsieur',
			'last_name': 'Patate', 
			}

		network_user.update_user_details(user_details)

		# Check that user creation was successful with correct user details
		self.assertEqual(network_user.user.email, user_details['email'])

		# Check that an email warning was sent following the creation
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].subject, "[Fiji] Monsieur Patate a créé un compte !")


		user_details = {
			'username': 'Monsieur Patate',
			'email': 'monsieur.carotte@gmail.com',
			'first_name': 'Monsieur',
			'last_name': 'Carotte', 
			}

		network_user.update_user_details(user_details)

		# Fetch the updated NetworkUser
		network_user = NetworkUser.objects.get(pk=network_user.pk)

		# Check that the user update was successful
		self.assertEqual(network_user.user.email, user_details['email'])