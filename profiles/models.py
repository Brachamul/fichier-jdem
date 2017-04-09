from django.db import models

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver

from fichiers_adherents.models import FichierAdherents, Adherent, Cnil, adherents_actuels


class Member(models.Model):

	id = models.IntegerField(primary_key=True)
	phoneless = models.BooleanField(default=False)

	def historique_adherent(self):
		return Adherent.objects.filter(num_adherent=self.id)

	def derniere_occurence_fichier(self):
		adherents = Adherent.objects.filter(num_adherent=self.id)
		fichier = FichierAdherents.objects.filter(adherent__in=adherents)
		return Adherent.objects.get(num_adherent=self.id, fichier=fichier.latest())


	def timeline(self):

		timeline = []

		#  notes
		notes = Note.objects.filter(member=self).values()
		for item in notes :
			item['category'] = 'note'
			timeline.append(item)

		# successful calls
		successful_calls = SuccessfulCall.objects.filter(member=self).values()
		for item in successful_calls :
			item['category'] = 'successful_call'
			timeline.append(item)

		# left messages 
		left_messages = LeftMessage.objects.filter(member=self).values()
		for item in left_messages :
			item['category'] = 'left_message'
			timeline.append(item)

		# wrong numbers 
		wrong_numbers = WrongNumber.objects.filter(member=self).values()
		for item in wrong_numbers :
			item['category'] = 'wrong_number'
			timeline.append(item)

		return timeline


	def __str__(self):
		return str(self.derniere_occurence_fichier())

	def initiate(fichier=False):
		''' Generate, for all fichiers or a single one, members for each adherent
		this is used when rebuilding the DB '''
		if fichier :
			adherents = Adherent.objects.filter(fichier=fichier)
		else :
			adherents = Adherent.objects.all()
		for adherent in adherents :
			new_member, created = Member.objects.get_or_create(id=adherent.num_adherent)

	def check_if_phoneless(self):
		''' Returns 'True' if the adherent has no phone number '''
		self.phoneless = self.derniere_occurence_fichier().phoneless()
		self.save()


@receiver(post_save, sender=Adherent)
def initiate_member(sender, instance, created, **kwargs):
	new_member, created = Member.objects.get_or_create(id=instance.num_adherent)
	new_member.check_if_phoneless()



# Timeline

# https://codepen.io/codyhouse/pen/FdkEf

class PhoningEvent(models.Model):

	member = models.ForeignKey(Member)
	operation = models.ForeignKey(Operation, blank=True, null=True)
	logged_by = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)

	event_type = models.CharField(max_length=64, choices=(
		('success', 'success'),
		('wrongnumber', 'wrongnumber'),
		('leftmessage', 'leftmessage'),
		('skip', 'skip')
		))

	def __str__(self):
		return self.text



class Note(models.Model):

	member = models.ForeignKey(Member)
	operation = models.ForeignKey(Operation, blank=True, null=True)
	logged_by = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)

	text = models.CharField(max_length=1024, blank=True, null=True)
	
	def __str__(self):
		return self.text