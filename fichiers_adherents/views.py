# -*- coding: utf-8 -*-
import csv, logging, sys, random, ast, json

import datetime as dt

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Max, F
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView



#	from datascope.models import mettre_a_jour_les_federations

from .models import *
from .forms import *
from . import emails

from profiles.models import Member

'''
@login_required
def dashboard(request):
	if request.user.has_perm('fichiers_adherents.peut_televerser'):
'''	


@login_required
def declaration_cnil(request):
	form_values = {}
	try : cnil = Cnil.objects.get(user=request.user)
	except ObjectDoesNotExist :
		if request.method == "POST":
			signature = request.POST.get('signature').lower()
			required_signature = "Lu et approuvé par {} {}".format(request.user.first_name, request.user.last_name).lower()
			lieu = request.POST.get('lieu')
			if signature == required_signature and lieu  :
				nouvelle_declaration = Cnil(user=request.user, lieu=lieu, signature=signature)
				nouvelle_declaration.save()
				messages.success(request, "Votre signature de la déclaration de confidentialité a bien été enregistrée.")
				return redirect('fichier')
			elif signature != required_signature or not lieu :
				if signature != required_signature :
					messages.error(request, 'Votre signature doit mentionner les mots : "{}"'.format(required_signature))
				if not lieu :
					messages.error(request, "Vous devez renseigner le lieu de signature.")
			else :
				messages.error(request, "Désolé, nous n'avons pas réussi à enregistrer votre signature.")
			form_values = {'lieu': lieu, 'signature': signature}
		return render(request, 'fichiers_adherents/cnil.html', form_values)
	else : return redirect('fichier')


@login_required
def televersement(request):
	if request.user.has_perm('fichiers_adherents.peut_televerser'):
		if request.method == "POST":
			upload_form = TéléversementDuFichierAdherentForm(request.POST, request.FILES)
			if upload_form.is_valid():
				date = request.POST.get('date')
				if not FichierAdherents.objects.filter(date=date) :
					fichier = request.FILES['fichier_csv']
					importateur = request.user
					fichier.name = ('fichiers_adherents/' + date + '_' + request.user.username + '.csv') # renomme le fichier
					date = dt.datetime.strptime(date, '%Y-%m-%d').date() # converts date from 'XXXX-XX-XX' format to datetime.date
					nouveau_fichier = FichierAdherents(importateur=importateur, fichier_csv=fichier, date=date) # rattache le fichier à la base des fichiers importés
					nouveau_fichier.save()
					try :
						importation(nouveau_fichier) # Importe les données du fichier dans la base "Adherent"
						Member.initiate(fichier=nouveau_fichier)
						emails.prevenir_du_chargement_dun_nouveau_fichier()
					except Exception as e:
						# UNEXPECTED ERROR
						messages.error(request, str(e))
						nouveau_fichier.delete() # Supprime le fichier et les adhérents associés
					else : 
						# SUCCESS !
						return redirect('visualisation_du_fichier_adherent', fichier_id=nouveau_fichier.id )
				else :
					# Fichier with date already exists
					messages.error(request, "Un fichier établit à la même date existe déjà dans la base !")
			else :
				# Form is not valid, overriding form with default empty form
				upload_form = TéléversementDuFichierAdherentForm()
				messages.error(request, "Le formulaire n'était pas valide.")
		else :
			# Request is not post, this is just the user accessing the page normally
			upload_form = TéléversementDuFichierAdherentForm()
		return render(request, 'fichiers_adherents/upload.html', {'upload_form': upload_form, 'page_title': "Téléverser un fichier adhérents"})
	else:
		# The user doesn't have the rights to access this page
		messages.error(request, "Vous n'avez pas les droits d'accès au téléversement du fichier des adhérents.")
		return redirect('admin')


@login_required
def visualisation_du_fichier_adherent(request, fichier_id):
	fichier = get_object_or_404(FichierAdherents, id=fichier_id)
	return render(request, 'fichiers_adherents/visualisation.html', {
		'page_title': "Visualisation d'un fichier adhérent",
		'fichier': fichier,
		})


@login_required
def query_checker(request):
	if request.user.has_perm('fichiers_adherents.lecture_fichier_national'):
		object_list = []
		query = "{}"
		if request.method == "POST":
			query = request.POST.get('query')
		try:
			query_dict = ast.literal_eval(query)
			object_list = adherents_actuels().filter(**query_dict)
		except Exception as e:
			messages.error(request, str(e))
		return render(request, 'fichiers_adherents/query_checker.html', {
			'page_title': "Query Checker",
			'query': query,
			'object_list': object_list,
			'admin_url': reverse('admin:fichiers_adherents_adherent_changelist'),
			})
	else :
		messages.error(request, "Vous n'avez pas le droit de lecture sur le fichier national des adhérents.")
		return redirect('/')




''' HELPER FUNCTIONS '''

@transaction.atomic # permet de charger tous les adherents en une seule fois, à la fin du traitement du fichier
def importation(fichier):

	# Lis le fichier CSV importé et crée une instance Adherent pour chacun d'entre eux

	current_row = 0
	with open(settings.MEDIA_ROOT + '/' + fichier.fichier_csv.name, encoding="cp1252", newline='') as fichier_ouvert:
		lecteur = csv.DictReader(fichier_ouvert, delimiter=";")
		for row in lecteur:
			current_row += 1
			nouvel_adherent, created = Adherent.objects.get_or_create(
				fichier=fichier,
				federation = row['Fédération'],
				date_premiere_adhesion = process_csv_date(row['Date première adhésion']),
				date_derniere_cotisation = process_csv_date(row['Date dernière cotisation']),
				num_adherent = row['Num adhérent'],
				genre = homme_ou_femme(row['Genre']),
				nom = row['Nom'],
				prenom = row['Prénom'],
				adresse1 = row['Adresse 1'],
				adresse2 = row['Adresse 2'],
				adresse3 = row['Adresse 3'],
				adresse4 = row['Adresse 4'],
				code_postal = row['Code postal'],
				ville = row['Ville'],
				pays = row['Pays'],
				npai = row['NPAI'],
				date_de_naissance = process_csv_date(row['Date de naissance']),
				profession = row['Profession'],
				tel_portable = row['Tel portable'],
				tel_bureau = row['Tel bureau'],
				tel_domicile = row['Tel domicile'],
				email = row['Email'].lower(),
				mandats = row['Mandats'].replace("\n", ", "),
				commune = row['Commune'],
				canton = row['Canton'],
				nouveau = process_csv_truth(row['Nouveau']),
				)

def process_csv_date(csv_date):
	if csv_date : return dt.datetime.strptime(csv_date, '%d/%m/%Y').date()
	else : return None

def process_csv_truth(csv_truth):
	if csv_truth == "oui" :
	else : return False


def homme_ou_femme(title):
	if title == "Mlle" or title == 'Mme' : return "F"
	elif title == "M." : return "H"
	else : return "?"


@method_decorator(login_required, name='dispatch')
class ListeDesAdherents(ListView):

	model = Adherent
	template_name = 'fichiers_adherents/fichier.html'

	def dispatch(self, request, *args, **kwargs):
		try : cnil = Cnil.objects.get(user=request.user)
		except ObjectDoesNotExist : return redirect('fichier__declaration_cnil')
		else: return super(ListeDesAdherents, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(ListeDesAdherents, self).get_context_data(**kwargs)
		context['adherents'] = adherents_visibles(self.request)
		context['page_title'] = 'Fichier des adhérents'
		context['csv'] = fichier_csv(self.request)
		context['list_actions'] = [
			{'text': 'Administrer', 'url': reverse('admin:fichiers_adherents_adherent_changelist')},
			]
		return context



def adherents_visibles(request):
	
	''' Renvoie la liste des adhérents actuels que l'utilisateur a le droit de voir '''
	
	droits = request.user.droits_set.all()
	if droits :
		# l'utilisateur dispose de droits de vue sur le fichier
		departements = set()
		for droits in droits :
			query = json.loads(droits.query)
			# query est un numéro de département ou une liste de numéros de départements
			if type(query) is list :
				# si c'est une liste, il y a plusieurs départements à ajouter
				for departement in query :
					departements.add(departement)
			else :
				departements.add(query)
		departements = list(departements) # convert set to list
		result = adherents_actuels().filter(federation__in=departements)
		return result
	else :
		# l'utilisateur ne dispose pas de droits de vue sur le fichier
		return []



@login_required
def VueAdherent(request, num_adherent):

	adherent = get_object_or_404(Adherent, num_adherent=num_adherent, fichier=FichierAdherents.objects.latest())
	if adherent in adherents_visibles(request) :

		if request.method == "POST" :
			num_adherent = request.POST.get('num_adherent')
			# Check if call was successful or not
			if request.POST.get('note') :
				new_note = Note(num_adherent=num_adherent, author=request.user, text=request.POST.get('note'))
				new_note.save()
				messages.success(request, "Votre note a été enregistrée.")

		return render(request, 'fichiers_adherents/adherent.html', {
			'adherent': adherent,
			'page_title': adherent.nom_courant(),
			})

	else :
		messages.error(request, "Vous n'êtes pas autorisé à consulter ce profil.")
		return redirect('fichier')



def fichier_csv(request):
	csvContent = "data:text/csv;charset=utf-8,\uFEFF"
	csvContent += "num_adherent; prenom; nom; federation; date_premiere_adhesion; date_derniere_cotisation; genre; adresse1; adresse2; adresse3; adresse4; code_postal; ville; pays; npai; date_de_naissance; profession; tel_portable; tel_bureau; tel_domicile; email; mandats; commune; canton;\n"
	for adherent in adherents_visibles(request):
		data = [
			str(adherent.num_adherent), adherent.prenom, adherent.nom,
			str(adherent.federation), str(adherent.date_premiere_adhesion), str(adherent.date_derniere_cotisation),
			adherent.genre, adherent.adresse1, adherent.adresse2, adherent.adresse3, adherent.adresse4,
			adherent.code_postal, adherent.ville, adherent.pays, adherent.npai, str(adherent.date_de_naissance),
			adherent.profession, adherent.tel_portable, adherent.tel_bureau, adherent.tel_domicile,
			adherent.email, adherent.mandats, adherent.commune, adherent.canton
			]
		csvContent += ";".join(data) + "\n"
	return csvContent



@method_decorator(staff_member_required, name='dispatch')
class DroitsDeLecture(ListView):

	model = Droits
	template_name = 'fichiers_adherents/droits_de_lecture.html'

	def get_context_data(self, **kwargs):
		context = super(DroitsDeLecture, self).get_context_data(**kwargs)
		context['page_title'] = "Droits de lecture du fichier des adhérents"
#		context['url_by_id'] = True
#		context['url_prefix'] = reverse('admin:fichiers_adherents_adherent_changelist') # changelist because addinng id after
		context['admin_url'] = reverse('admin:fichiers_adherents_droits_changelist')
		return context
