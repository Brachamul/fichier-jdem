# -*- coding: utf-8 -*-

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import os
from django.utils.text import slugify
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class FichierAdherents(models.Model):

	date_d_import = models.DateTimeField(auto_now_add=True)
	importateur = models.ForeignKey(User)
	slug = models.SlugField(max_length=255)
	fichier_csv = models.FileField(upload_to='fichiers_adherents/')
	nombre_nouveaux_adherents = models.PositiveSmallIntegerField(null=True, blank=True, default=0)
	nombre_readhesions = models.PositiveSmallIntegerField(null=True, blank=True, default=0)

	def adherents(self) :
		''' liste les adherents ayant été importés par ce fichier '''
		return AdherentDuFichier.objects.filter(fichier=self)

	def nouveaux_adherents(self) :
		''' liste le nombre d'adhérents qui seraient introduits par ce fichier '''
		nouveaux_adherents = []
		for adherent in self.adherents():
			if adherent.est_nouveau() : nouveaux_adherents.append(adherent)
		return nouveaux_adherents

	def adherents_maj(self) :
		''' liste le nombre d'adhérents qui ont réadhéré '''
		adherents_maj = []
		for adherent in self.adherents():
			try : adherent_actuel_correspondant = Adherent.objects.get(num_adherent=adherent.num_adherent)
			except Adherent.DoesNotExist : pass
			else : 
				if adherent.date_derniere_cotisation != adherent_actuel_correspondant.date_derniere_cotisation :
					# si l'adhérent existe et qu'il a réadhéré
					adherents_maj.append(adherent)
		return adherents_maj

	def date_ultime(self) :
		''' cherche la dernière date mentionnée dans le fichier '''
		latest_entry = self.adherents().latest('date_derniere_cotisation')
		return latest_entry.date_derniere_cotisation

	def jours_depuis_le_fichier_precedent(self) :
		try : date_actuelle = Adherent.objects.latest('date_derniere_cotisation').date_derniere_cotisation
		except Adherent.DoesNotExist : return False
		else :
			jours = (date_actuelle - self.date_ultime()).days
			return jours

	def __str__(self):
		return self.slug

	class Meta:
		verbose_name_plural = 'fichiers adhérents'.encode('utf-8')
		permissions = (('peut_televerser', 'peut téléverser'),)
		# if request.user.has_perm('fichiers_adhérents.peut_televerser')



class Adherent(models.Model):
	# Ce profil reprend une partie des données du fichier adhérent officiel du MoDem. Il ne peut pas être modifié par l'utilisateur
	federation = models.IntegerField(null=True, blank=True)
	date_premiere_adhesion = models.DateField(null=True, blank=True)
	date_derniere_cotisation = models.DateField(null=True, blank=True)
	num_adherent = models.IntegerField(primary_key=True)
	genre = models.CharField(max_length=5, null=True, blank=True)
	nom = models.CharField(max_length=255, null=True, blank=True)
	prenom = models.CharField(max_length=255, null=True, blank=True)
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
	commune = models.CharField(max_length=255, null=True, blank=True) # Dans le cas où la personne est élu dans une autre commune que sa ville de résidence.
	canton = models.CharField(max_length=255, null=True, blank=True)
	importe_par_le_fichier = models.ForeignKey(FichierAdherents, null=True, blank=True, on_delete=models.SET_NULL)

	def anciennete(self): return datetime.now() - self.date_premiere_adhesion
	def actif(self): return (datetime.now().year - self.date_derniere_cotisation.year) > settings.DUREE_D_ACTIVITE
	def jours_depuis_la_derniere_cotisation(self): return (datetime.now().date() - self.date_derniere_cotisation).days
	def nom_courant(self):
		try : return self.prenom + " " + self.nom
		except NameError : return "Anonyme"

	def __str__(self): return '{} {}'.format(self.prenom, self.nom)

	class Meta:
		ordering = ['nom']
		verbose_name = "adhérent".encode('utf-8')
		verbose_name_plural = 'adhérents'.encode('utf-8')



class DateDeCotisation(models.Model):

	date = models.DateTimeField()
	adherents = models.ManyToManyField(Adherent, related_name='adherents_du_jour')

	def __str__(self): return self.date.strftime('%Y-%m-%d')

	class Meta:
		verbose_name = "date de cotisation".encode('utf-8')
		verbose_name_plural = "dates de cotisation".encode('utf-8')
		ordering = ['-date']



class AdherentDuFichier(models.Model):

	fichier = models.ForeignKey(FichierAdherents)
	adherent = models.ForeignKey(Adherent, null=True)
	federation = models.IntegerField(null=True, blank=True)
	date_premiere_adhesion = models.DateField(null=True, blank=True)
	date_derniere_cotisation = models.DateField(null=True, blank=True)
	num_adherent = models.IntegerField(primary_key=True)
	genre = models.CharField(max_length=5, null=True, blank=True)
	nom = models.CharField(max_length=255, null=True, blank=True)
	prenom = models.CharField(max_length=255, null=True, blank=True)
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
	commune = models.CharField(max_length=255, null=True, blank=True) # Dans le cas où la personne est élu dans une autre commune que sa ville de résidence.
	canton = models.CharField(max_length=255, null=True, blank=True)

	def est_nouveau(self):
		try : adherent_actuel_correspondant = Adherent.objects.get(num_adherent=self.num_adherent)
		except Adherent.DoesNotExist : return True
		else : return False

	def transferer_les_donnees_dun_adherent_du_fichier(self, adherent_de_la_base):
		''' transfère les données du fichier adhérent vers la base '''
		adherent_de_la_base.federation					= self.federation
		adherent_de_la_base.date_premiere_adhesion		= self.date_premiere_adhesion
		adherent_de_la_base.date_derniere_cotisation	= self.date_derniere_cotisation
		adherent_de_la_base.genre 						= self.genre
		adherent_de_la_base.nom 						= self.nom
		adherent_de_la_base.prenom 						= self.prenom
		adherent_de_la_base.adresse1 					= self.adresse1
		adherent_de_la_base.adresse2 					= self.adresse2
		adherent_de_la_base.adresse3 					= self.adresse3
		adherent_de_la_base.adresse4 					= self.adresse4
		adherent_de_la_base.code_postal 				= self.code_postal
		adherent_de_la_base.ville 						= self.ville
		adherent_de_la_base.pays 						= self.pays
		adherent_de_la_base.npai 						= self.npai
		adherent_de_la_base.date_de_naissance 			= self.date_de_naissance
		adherent_de_la_base.profession 					= self.profession
		adherent_de_la_base.tel_portable 				= self.tel_portable
		adherent_de_la_base.tel_bureau 					= self.tel_bureau
		adherent_de_la_base.tel_domicile 				= self.tel_domicile
		adherent_de_la_base.email 						= self.email
		adherent_de_la_base.mandats 					= self.mandats
		adherent_de_la_base.commune 					= self.commune
		adherent_de_la_base.canton 						= self.canton

		adherent_de_la_base.importe_par_le_fichier 		= self.fichier
		adherent_de_la_base.save()

		date_de_cotisation,created = DateDeCotisation.objects.get_or_create(date=self.date_derniere_cotisation)
		adherent_de_la_base.dates_de_cotisation.add(date_de_cotisation)
		# permet de sauvegarder un historique des cotisations


	def creer_un_nouvel_adherent(self):
		''' Ajoute un adhérent du fichier importé à la base '''
		nouvel_adherent = Adherent(num_adherent=self.num_adherent)
		self.transferer_les_donnees_dun_adherent_du_fichier(nouvel_adherent)
		nouvel_adherent.save()
	
	def mettre_a_jour_un_adherent(self):
		''' Met à jour les adhérents existants avec les données du fichier importé '''
		adherent_maj = Adherent.objects.get(num_adherent=self.num_adherent)
		self.transferer_les_donnees_dun_adherent_du_fichier(adherent_maj)

	def __str__(self): return ('%s %s') % (self.prenom, self.nom)

	class Meta:
		verbose_name = "adhérent du fichier".encode('utf-8')
		verbose_name_plural = "adhérents du fichier".encode('utf-8')
		ordering = ['nom']



class Note(models.Model):

	target = models.ForeignKey(Adherent, related_name='notes')
	author = models.ForeignKey(User)
	text = models.CharField(max_length=1024)
	date = models.DateTimeField(auto_now_add=True)
	
	def __str__(self): return self.text