from django.test import TestCase, Client

from datetime import datetime, timedelta
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


from django.contrib.auth.models import User
from fichiers_adherents.models import *


class TestObjectCreations(TestCase):

	def setUp(self):

		self.today = datetime.now().date()
		self.test_user = User.objects.create(username="Monsieur Patate")
		self.test_fichier = FichierAdherents.objects.create(date=self.today, importateur=self.test_user)

	def test_signal_verifier_si_a_jour(self):

		test_adherent = Adherent.objects.create(
			fichier = self.test_fichier,
			num_adherent = 999999,
			prenom = "Monsieur",
			nom = "Patate",
			date_derniere_cotisation = datetime.now().date() - timedelta(days = 100),
			)

		self.assertEqual(test_adherent.a_jour_de_cotisation, True)