# -*- coding: utf-8 -*-

import os, uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.db.models import Max, F
from django.dispatch import receiver

import datetime as dt



class FichierAdherents(models.Model):

	date_d_import = models.DateTimeField(auto_now_add=True)
	date = models.DateField()
	importateur = models.ForeignKey(User)
	fichier_csv = models.FileField(upload_to='fichiers_adherents/', null=True)

	def delete(self,*args,**kwargs):
		# TODO : Doesn't seem to work :(
		if os.path.isfile(self.fichier_csv.path):
			os.remove(self.fichier_csv.path)

		super(FichierAdherents, self).delete(*args,**kwargs)

	def adherents_a_jour(self) :
		''' liste les adherents ayant été importés par ce fichier '''
		return self.adherent_set.filter(a_jour_de_cotisation=True)

	def fichier_precedent(self) :
		return self.get_previous_by_date()

	def nouveaux_adherents(self) :
		''' liste le nombre d'adhérents qui seraient introduits par ce fichier '''
		nouveaux_adherents = []
		for adherent in self.adherents_a_jour():
			if adherent.est_nouveau() :
				nouveaux_adherents.append(adherent)
		return nouveaux_adherents

	def resubbed(self) :
		''' liste le nombre d'adhérents qui ont réadhéré '''
		result = []
		for adherent in self.adherent_set.all():
			if adherent.has_resubbed(fichier=self) :
				result.append(adherent)
		return result

	def expired(self):
		''' liste le nombre d'adhérents qui n'ont pas réadhéré '''
		result = []
		try :
			fichier_precedent = self.get_previous_by_date()
		except FichierAdherents.DoesNotExist :
			return result
		else :
			for adherent in fichier_precedent.adherents_a_jour():
				# pour chaque adhérent à jour dans le fichier précédent
				# on regarde s'il existe toujours et est à jour dans le fichier actuel
				try :
					Adherent.objects.get(
						fichier=self,
						num_adherent=adherent.num_adherent,
						a_jour_de_cotisation=True
						)
				except Adherent.DoesNotExist :
					result.append(adherent)
			return result

	def date_de_ce_fichier(self) :
		''' cherche la dernière date mentionnée dans le fichier '''
		latest_entry = self.adherent_set.latest()
		return latest_entry.date_derniere_cotisation

	def jours_depuis_le_fichier_precedent(self) :
		try :
			fichier_precedent = self.get_previous_by_date()
		except FichierAdherents.DoesNotExist :
			return False
		else :
			return (self.date - fichier_precedent.date).days

	def __str__(self):
		return "Fichier du {}, importé le {} par {}".format(self.date, self.date_d_import.date(), self.importateur)

	class Meta:
		ordering = ['-date']
		get_latest_by = 'date'
		verbose_name = 'fichier'
		verbose_name_plural = 'fichiers'
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
	a_jour_de_cotisation = models.BooleanField(default=False)
	trop_vieux = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		self.a_jour_de_cotisation = self.calculer_si_actif()
		self.trop_vieux = self.calculer_si_trop_vieux()
		super(Adherent, self).save(*args, **kwargs)

	# Utilitaires
	
	def anciennete(self):
		if self.date_premiere_adhesion :
			return dt.datetime.now().date() - self.date_premiere_adhesion
		else:
			return None
	
	def jours_depuis_la_derniere_cotisation(self):
		return (dt.datetime.now().date() - self.date_derniere_cotisation).days

	def nom_courant(self):
		try : return self.prenom + " " + self.nom
		except NameError : return "Anonyme"

	def est_nouveau(self):
		# regarde si l'adhérent existait déjà dans le fichier précédent
		try :
			adherent_ancien = Adherent.objects.get(fichier=self.fichier.get_previous_by_date(), num_adherent=self.num_adherent)
		except (Adherent.DoesNotExist, FichierAdherents.DoesNotExist) :
			return True
		else :
			return False

	def est_recent(self):
		if self.anciennete() :
			return self.anciennete().days < 90
		else :
			return False

	def has_resubbed(self, fichier):
		# regarde si l'adhérent a réadhéré depuis le fichier précédent
		try :
			adherent_ancien = Adherent.objects.get(fichier=fichier.get_previous_by_date(), num_adherent=self.num_adherent)
		except (Adherent.DoesNotExist, FichierAdherents.DoesNotExist) :
			return False
		else :
			return adherent_ancien.date_derniere_cotisation < self.date_derniere_cotisation

	def calculer_si_actif(self):
		derniere_cotisation = self.date_derniere_cotisation
		if isinstance(derniere_cotisation, dt.datetime) : # for some reason the datefield sometimes contains datetime values
			derniere_cotisation = derniere_cotisation.date()
		return derniere_cotisation.year >= self.fichier.date.year - 2 # l'année en cours, la précédente et celle d'avant

	def calculer_si_trop_vieux(self):
		naissance = self.date_de_naissance
		if not naissance : return True # sans date, on considère que l'adhérent est trop âgé
		if isinstance(naissance, dt.datetime) : # for some reason the datefield sometimes contains datetime values
			naissance = naissance.date()
		return naissance < dt.datetime.now().date() - dt.timedelta(days=365.25*33) # 33 ans

	def phoneless(self):
		if self.tel_portable or self.tel_bureau or self.tel_domicile :
			return False
		else :
			return True


	# Meta

	def __str__(self): return '{} {}'.format(self.prenom, self.nom)

	class Meta:
		ordering = ['nom']
		get_latest_by = "fichier"
		permissions = (('lecture_fichier_national', 'peut lire le fichier national'),)
		verbose_name = "adhérent".encode('utf-8')
		verbose_name_plural = 'adhérents'.encode('utf-8')



def adherents_actuels() :
	
	''' Renvoie la liste des adhérents actuels, c'est à dire
	provenant du fichier le plus récent, et ayant adhéré
	ou réadhéré moins de 2 ans plus tôt.'''

	try :
		dernier_fichier = FichierAdherents.objects.latest()
	except FichierAdherents.DoesNotExist :
		return Adherent.objects.all() # empty queryset
	else :
		return Adherent.objects.filter(
			fichier=dernier_fichier,
			a_jour_de_cotisation=True,
			trop_vieux=False,
			)



class Droits(models.Model):

	''' Un groupe d'adhérents définis par une requête, auquel on peut attacher
	des lecteurs qui auront droit d'accès pour lire ces membres dans leur fichier '''

	name = models.CharField(max_length=250)
	readers = models.ManyToManyField(User, through='Reader')
	query = models.CharField(max_length=5000) # ex : {'federation__in': [8,10,51,52,54,55,57,67,68,88], 'date_derniere_cotisation__year':'2016'}

	class Meta:
		ordering = ['name']
		verbose_name = "droit d'accès".encode('utf-8')
		verbose_name_plural = "droits d'accès".encode('utf-8')

	def __str__(self): return self.name



class Reader(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	droits = models.ForeignKey(Droits, on_delete=models.CASCADE)
	date = models.DateTimeField(auto_now=True)
	class Meta :
		verbose_name = "Lecteur"
		def __str__(self): return str(self.user)



class Cnil(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	signature = models.CharField(max_length=255)
	lieu = models.CharField(max_length=255, verbose_name="fait à")
	date = models.DateTimeField(auto_now_add=True)
	class Meta :
		verbose_name = "Déclaration CNIL"
		verbose_name_plural = "Déclarations CNIL"
	def __str__(self): return str(self.user)