from django.test import TestCase, Client

import datetime as dt
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from fichiers_adherents.models import Adherent, FichierAdherents, Note, WrongNumber
from phoning.models import Operation

class CoordoneesTestCase(TestCase):

	def setUp(self):

		self.client = Client()


		self.today = dt.datetime.now().date()
		self.test_user = User.objects.create_user('MonsieurPatate', 'monsieur.patate@potato.farm', 'potato')
		self.test_fichier = FichierAdherents.objects.create(date=self.today, importateur=self.test_user)

		operation = Operation.objects.create(
			name="Opé Test",
			query="{ 'federation': 64, }",
			valid_until=dt.datetime.now() + dt.timedelta(days=1),
			created_by=self.test_user,
			)
		operation.authorized_users.add(self.test_user)

		Adherent.objects.create(
			fichier=self.test_fichier,
			num_adherent=999999,
			prenom="Monsieur",
			nom="Patate",
			federation=78,
			date_premiere_adhesion=dt.datetime(2014,3,12),
			date_derniere_cotisation=dt.datetime(2016,5,16),
			date_de_naissance=dt.datetime(1991,5,4),
			tel_portable="06 72 82 17 28",
			)

		Adherent.objects.create(
			fichier=self.test_fichier,
			num_adherent=999998,
			prenom="Madame",
			nom="Patate",
			federation=64,
			date_premiere_adhesion=dt.datetime(2015,6,13),
			date_derniere_cotisation=dt.datetime(2016,8,31),
			date_de_naissance=dt.datetime(1993,3,30),
			tel_portable="06 72 82 17 27",
			)


	def test_coordonees_can_be_displayed(self):
		operation = Operation.objects.get(name="Opé Test")
		login = self.client.login(username='MonsieurPatate', password='potato')
		url = reverse('coordonnees', kwargs={'operation_id': operation.pk})
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)