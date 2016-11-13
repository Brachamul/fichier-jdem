# -*- coding: utf-8 -*-

import os, uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Max, F

from datetime import datetime, timedelta


class FichierAdherents(models.Model):

	date_d_import = models.DateTimeField(auto_now_add=True)
	date = models.DateField()
	importateur = models.ForeignKey(User)
	fichier_csv = models.FileField(upload_to='fichiers_adherents/')

	def delete(self,*args,**kwargs):
		# TODO : Doesn't seem to work :(
		if os.path.isfile(self.fichier_csv.path):
			os.remove(self.fichier_csv.path)

		super(FichierAdherents, self).delete(*args,**kwargs)

	def adherents(self) :
		''' liste les adherents ayant été importés par ce fichier '''
		return Adherent.objects.filter(fichier=self)

	def nouveaux_adherents(self) :
		''' liste le nombre d'adhérents qui seraient introduits par ce fichier '''
		nouveaux_adherents = []
		for adherent in self.adherents():
			if adherent.is_new(fichier=self) :
				nouveaux_adherents.append(adherent)
		return nouveaux_adherents

	def resubbed(self) :
		''' liste le nombre d'adhérents qui ont réadhéré '''
		adherents_maj = []
		for adherent in self.adherents():
			if adherent.has_resubbed(fichier=self) :
				adherents_maj.append(adherent)
		return adherents_maj

	def expired(self):
		expiration_window_end = self.date_de_ce_fichier() - timedelta(days=730) # 2 years
		expiration_window_start = expiration_window_end - timedelta(days=self.jours_depuis_le_fichier_precedent())
		expired_people = Adherent.objects.filter(
			date_derniere_cotisation__lt = expiration_window_end,
			date_derniere_cotisation__gt = expiration_window_start
			)
		return expired_people

	def date_de_ce_fichier(self) :
		''' cherche la dernière date mentionnée dans le fichier '''
		latest_entry = self.adherents().latest()
		return latest_entry.date_derniere_cotisation

	def jours_depuis_le_fichier_precedent(self) :
		try : date_du_fichier_actuel = Adherent.objects.exclude(fichier=self).latest().date_derniere_cotisation
		except Adherent.DoesNotExist :
			return False
		else :
			return (self.date_de_ce_fichier() - date_du_fichier_actuel).days

	def __str__(self):
		return "Fichier du {}, importé le {} par {}".format(self.date, self.date_d_import.date(), self.importateur)

	class Meta:
		get_latest_by = "date_derniere_cotisation"
		verbose_name_plural = 'fichiers adhérents'.encode('utf-8')
		permissions = (('peut_televerser', 'peut charger les nouveaux fichiers adhérents'),)
		# if request.user.has_perm('fichiers_adhérents.peut_televerser')



class Adherent(models.Model):
	'''
	Ce profil reprend une partie des données du fichier adhérent officiel du MoDem. Il ne peut pas être modifié par l'utilisateur
	A chaque fois qu'un fichier est chargé et que des nouveaux adhérents,
	ou des mises à jour d'adhérents sont détéctés, on créé une nouvelle instance d'Adhérent.
	Un adhérent peut ainsi avoir plusieurs instances, représentant l'historique de son parcours.
	'''
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # UUID instead of normal incremental ID
	fichier = models.ForeignKey(FichierAdherents, null=True, blank=True, on_delete=models.CASCADE)
	num_adherent = models.IntegerField(verbose_name="Numéro d'adhérent")
	prenom = models.CharField(max_length=255, null=True, blank=True)
	nom = models.CharField(max_length=255, null=True, blank=True)
	federation = models.IntegerField(null=True, blank=True)
	date_premiere_adhesion = models.DateField(null=True, blank=True)
	date_derniere_cotisation = models.DateField(null=True, blank=True)
	genre = models.CharField(max_length=5, null=True, blank=True)
	adresse1 = models.CharField(max_length=1000, null=True, blank=True)
	adresse2 = models.CharField(max_length=1000, null=True, blank=True)
	adresse3 = models.CharField(max_length=1000, null=True, blank=True)
	adresse4 = models.CharField(max_length=1000, null=True, blank=True)
	code_postal = models.CharField(max_length=255, null=True, blank=True)
	ville = models.CharField(max_length=255, null=True, blank=True)
	pays = models.CharField(max_length=255, null=True, blank=True)
	npai = models.CharField(max_length=255, null=True, blank=True)
	date_de_naissance = models.DateField(null=True, blank=True)
	profession = models.CharField(max_length=255, null=True, blank=True)
	tel_portable = models.CharField(max_length=255, null=True, blank=True)
	tel_bureau = models.CharField(max_length=255, null=True, blank=True)
	tel_domicile = models.CharField(max_length=255, null=True, blank=True)
	email = models.CharField(max_length=255, null=True, blank=True)
	mandats = models.CharField(max_length=255, null=True, blank=True)
	commune = models.CharField(max_length=255, null=True, blank=True) # Dans le cas où la personne est élue dans une autre commune que sa ville de résidence.
	canton = models.CharField(max_length=255, null=True, blank=True)
	actuel = models.BooleanField(default=False) # valeur calculée, voir actualisation_des_adherents()



	# Utilitaires
	
	def anciennete(self):
		return datetime.now() - self.date_premiere_adhesion
	
	def actif(self):
		return (datetime.now().year - self.date_derniere_cotisation.year) > settings.DUREE_D_ACTIVITE

	def jours_depuis_la_derniere_cotisation(self):
		return (datetime.now().date() - self.date_derniere_cotisation).days

	def nom_courant(self):
		try : return self.prenom + " " + self.nom
		except NameError : return "Anonyme"

	def is_new(self, fichier):
		try : adherent_actuel_correspondant = Adherent.objects.filter(num_adherent=self.num_adherent).exclude(fichier=fichier).latest()
		except Adherent.DoesNotExist : return True
		else : return False

	def has_resubbed(self, fichier):
		try : adherent_actuel_correspondant = Adherent.objects.filter(num_adherent=self.num_adherent).exclude(fichier=fichier).latest()
		except Adherent.DoesNotExist : return False
		else : return adherent_actuel_correspondant.date_derniere_cotisation < self.date_derniere_cotisation



	# Meta

	def __str__(self): return '{} {}'.format(self.prenom, self.nom)

	class Meta:
		ordering = ['nom']
		get_latest_by = "date_derniere_cotisation"
		permissions = (('lecture_fichier_national', 'peut lire le fichier national'),)
		verbose_name = "adhérent".encode('utf-8')
		verbose_name_plural = 'adhérents'.encode('utf-8')


def actualisation_des_adherents() :
	'''
	Les adhérents ont chacun plusieurs lignes dans la base, puisque leurs données
	sont copiées à chaque import du fichier. Cette fonction sélectionne, pour chaque adhérent,
	une seule ligne considéré comme la plus à jour, et la marque d'un "actuel=True"
	'''
	Adherent.objects.all().update(actuel=False) # Reset
	for adherent in Adherent.objects.values('num_adherent').annotate(date_du_ficher=Max('fichier__date')) :
		adherent = Adherent.objects.get(num_adherent=adherent['num_adherent'], fichier__date=adherent['date_du_ficher'])
		adherent.actuel = True
		adherent.save()
		print(adherent)




class Note(models.Model):

	# todo : activate that
	target = models.ForeignKey(Adherent, related_name='notes')
	author = models.ForeignKey(User)
	text = models.CharField(max_length=1024)
	date = models.DateTimeField(auto_now_add=True)
	
	def __str__(self): return self.text



class WrongNumber(models.Model):

	# todo : fix that
	adherent = models.ForeignKey(Adherent)
	reported_by = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self): return self.adherent



class Droits(models.Model):
	name = models.CharField(max_length=250)
	users = models.ManyToManyField(User)
	query = models.CharField(max_length=5000) # ex : {'federation__in': [8,10,51,52,54,55,57,67,68,88], 'date_derniere_cotisation__year':'2016'}

	class Meta:
		verbose_name = "droit d'accès".encode('utf-8')
		verbose_name_plural = "droits d'accès".encode('utf-8')

	def __str__(self): return self.name