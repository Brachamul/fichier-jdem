import uuid
from django.test import TestCase, Client

from django.contrib.auth.models import User
from django_auth_network_client.models import NetworkUser


class NetworkUserTestCase(TestCase):


	def setUp(self):

		self.test_user = User.objects.create(username="Monsieur Patate", email="monsieur.patate@gmail.com")
		self.test_network_user = NetworkUser.objects.create(user=self.test_user, uuid=uuid.uuid4())


	def test__update_user_details__new_user(self):

		network_user, created = NetworkUser.objects.get_or_create(uuid=uuid.uuid4())

		user_details = {
			'username': 'Monsieur Patate',
			'email': 'monsieur.patate@gmail.com',
			'first_name': 'Monsieur',
			'last_name': 'Patate', 
			}

		network_user.update_user_details(user_details)

		self.assertEqual(network_user.user.email, user_details['email'])


	def test__update_user_details__existing_user(self):

		user_details = {
			'username': 'Madame Patate',
			'email': 'madame.patate@gmail.com',
			}

		self.test_network_user.update_user_details(user_details)

		print('network_user.user.email : ' + self.test_network_user.user.email)
		print('input user details : ' + user_details['email'])

		self.assertEqual(self.test_network_user.user.email, user_details['email'])