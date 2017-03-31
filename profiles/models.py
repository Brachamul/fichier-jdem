from django.db import models

from django.core.exceptions import ObjectDoesNotExist

from fichiers_adherents.models import FichierAdherents, Adherent, Cnil


class Member(models.Model):

	id = models.IntegerField(primary_key=True)

	def historique_adherent(self):
		return Adherent.objects.filter(num_adherent=self.id)

	def derniere_occurence_fichier(self):
		return Adherent.objects.get(num_adherent=self.id, fichier=FichierAdherents.objects.latest()) # Todo : what if not in latest fichier ?

	def __str__(self):
		return str(self.id)

	def initiate(fichier=False):
		''' Generate, for all fichiers or a single one, members for each adherent '''
		if fichier :
			adherents = Adherent.objects.filter(fichier=fichier)
		else :
			adherents = Adherent.objects.all()
		for adherent in adherents :
			new_member, created = Member.objects.get_or_create(id=adherent.num_adherent)

# https://codepen.io/codyhouse/pen/FdkEf
