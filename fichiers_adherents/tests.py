from django.test import TestCase, Client

from datetime import datetime, timedelta
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


from django.contrib.auth.models import User
from fichiers_adherents.models import *


class AdherentTestCase(TestCase):

	def setUp(self):

		self.today = datetime.now().date()
		self.test_user = User.objects.create(username="Monsieur Patate")
		self.test_fichier = FichierAdherents.objects.create(date=self.today, importateur=self.test_user)

	def test_calculer_si_actif_on_save(self):

		test_adherent = Adherent.objects.create(
			fichier = self.test_fichier,
			num_adherent = 999999,
			prenom = "Monsieur",
			nom = "Patate",
			date_derniere_cotisation = datetime.now().date() - timedelta(days = 100),
			)

		self.assertEqual(test_adherent.a_jour_de_cotisation, True)