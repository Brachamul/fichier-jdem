from django.test import TestCase, Client

import datetime
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from fichiers_adherents.models import Adherent, Note, WrongNumber
from phoning.models import Operation

class CoordoneesTestCase(TestCase):

	def setUp(self):

		self.client = Client()

		self.user = User.objects.create_user('YooZer', 'yoo.zer@userweb.com', 'password')

		operation = Operation.objects.create(
			name="Opé Test",
			query="{ 'federation': 64, }",
			valid_until=datetime.datetime.now() + datetime.timedelta(days=1),
			created_by=self.user,
			)
		operation.authorized_users.add(self.user)

		Adherent.objects.create(
			num_adherent=999999, prenom="Monsieur", nom="Patate",
			federation=64,
			date_premiere_adhesion=datetime.datetime(2014,3,12),
			date_derniere_cotisation=datetime.datetime(2016,5,16),
			date_de_naissance=datetime.datetime(1991,5,4),
			tel_portable="06 72 82 17 28"
			)

		Adherent.objects.create(
			num_adherent=999998, prenom="Madame", nom="Patate",
			federation=64,
			date_premiere_adhesion=datetime.datetime(2015,6,13),
			date_derniere_cotisation=datetime.datetime(2016,8,31),
			date_de_naissance=datetime.datetime(1993,3,30),
			tel_portable="06 72 82 17 27"
			)


	def test_coordonees_can_be_displayed(self):
		operation = Operation.objects.get(name="Opé Test")
		self.client.login(username='YooZer', password='password')
		url = reverse('coordonnees', kwargs={'operation_id': operation.pk})
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)