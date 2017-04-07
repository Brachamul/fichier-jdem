from django.db import models

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from fichiers_adherents.models import FichierAdherents, Adherent, Cnil, adherents_actuels



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


@receiver(post_save, sender=Adherent)
def initiate_member(sender, instance, created, **kwargs):
	new_member, created = Member.objects.get_or_create(id=instance.num_adherent)



class Note(models.Model):

	member = models.ForeignKey(Member)
	author = models.ForeignKey(User)
	text = models.CharField(max_length=1024)
	date = models.DateTimeField(auto_now_add=True)
	
	def __str__(self): return self.text


# https://codepen.io/codyhouse/pen/FdkEf
