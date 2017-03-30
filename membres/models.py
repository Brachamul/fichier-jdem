from django.db import models

from fichiers_adherents.models import Adherent

class Membre(models.Model):

	id = models.IntegerField(primary_key=True)

	def historique_adherent(self):
		return Adherent.objects.filter(num_adherent=self.id)


# https://codepen.io/codyhouse/pen/FdkEf