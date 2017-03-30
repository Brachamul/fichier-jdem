from django.db import models

from django.core.exceptions import ObjectDoesNotExist
from fichiers_adherents.models import Adherent, FichierAdherents

class Member(models.Model):

	id = models.IntegerField(primary_key=True)

	def historique_adherent(self):
		return Adherent.objects.filter(num_adherent=self.id)

	def derniere_occurence_fichier(self):
		return Adherent.objects.get(num_adherent=self.id, fichier=Fichier.objects.latest()) # what if not in latest fichier ?

	def __str__(self):
		return str(self.id)



# https://codepen.io/codyhouse/pen/FdkEf

def generate_members():
	for adherent in Adherent.objects.all() :
		new_member, created = Member.objects.get_or_create(id=adherent.num_adherent)