# -*- coding: utf-8 -*-
import csv, logging, sys, random, ast, json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Max, F
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView


#	from datascope.models import mettre_a_jour_les_federations

from .models import *
from .forms import *

'''
@login_required
def dashboard(request):
	if request.user.has_perm('fichiers_adherents.peut_televerser'):
'''	


@login_required
def televersement(request):
	if request.user.has_perm('fichiers_adherents.peut_televerser'):
		if request.method == "POST":
			upload_form = TéléversementDuFichierAdherentForm(request.POST, request.FILES)
			if upload_form.is_valid():
				logging.info("A new adherent file was uploaded by {user}.".format(user=request.user).encode('utf8'))
				fichier = request.FILES['fichier_csv']
				importateur = request.user
				date = request.POST.get('date')
				fichier.name = ('fichiers_adherents/' + date + '_' + request.user.username + '.csv') # renomme le fichier
				nouveau_fichier = FichierAdherents(importateur=importateur, fichier_csv=fichier, date=date) # rattache le fichier à la base des fichiers importés
				nouveau_fichier.save()
				importation(nouveau_fichier) # Importe les données du fichier dans la base "Adherent"
				actualisation_des_adherents()
				return redirect('visualisation_du_fichier_adherent', fichier_id=nouveau_fichier.id )
			else:
				return render(request, 'fichiers_adherents/upload.html', {'upload_form': upload_form, 'page_title': "Téléverser un fichier adhérents"})
		else:
			upload_form = TéléversementDuFichierAdherentForm()
			return render(request, 'fichiers_adherents/upload.html', {'upload_form': upload_form, 'page_title': "Téléverser un fichier adhérents"})
	else:
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
			object_list = Adherent.objects.filter(**query_dict)
		except ValueError as e:
			messages.error(request, repr(e))
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
				)

def process_csv_date(csv_date):
	if csv_date : return datetime.strptime(csv_date, '%d/%m/%Y').date()
	else : return None

def homme_ou_femme(title):
	if title == "Mlle" or title == 'Mme' : return "F"
	elif title == "M." : return "H"
	else : return "?"

def adherents_actifs() :
	''' liste le nombre d'adhérents qui seraient introduits par ce fichier '''
	return Adherent.objects.annotate(max_date=Max('date_derniere_cotisation')).filter(date_derniere_cotisation=F('max_date'))
	# can't use Adherent.objects.all().order_by('date_derniere_cotisation').distinct('num_adherent') on sqlite, so using .values_list('num_adherent', flat=True).distinct() instead


@method_decorator(login_required, name='dispatch')
class ListeDesAdherents(ListView):

	model = Adherent
	template_name = 'list.html'

	def get_context_data(self, **kwargs):

		context = super(ListeDesAdherents, self).get_context_data(**kwargs)
		context['object_list'] = Adherent.objects.filter(actuel=True)
		context['list_actions'] = [
			{'text': 'Actualiser', 'url': reverse('fichier__actualiser')},
			{'text': 'Administrer', 'url': reverse('admin:fichiers_adherents_adherent_changelist')},
			]
		context['page_title'] = 'Liste des Adhérents'
		context['url_by_id'] = True
		return context



def actualiser_les_adherents(request) :
	if request.user.has_perm('fichiers_adherents.peut_televerser'):
		actualisation_des_adherents()
		return redirect('fichier__adherents')
	else:
		messages.error(request, "Vous n'avez pas les droits d'accès au téléversement du fichier des adhérents.")
		return redirect('/')

@method_decorator(login_required, name='dispatch')
class Fichier(ListView):

	model = Adherent
	template_name = 'fichiers_adherents/fichier.html'

	def get_context_data(self, **kwargs):
		context = super(Fichier, self).get_context_data(**kwargs)

		droits = self.request.user.droits_set.all()
		departements = set()
		for droits in droits :
			query = json.loads(droits.query)
			if type(query) is list :
				for departement in query :
					departements.add(departement)
			else :
				departements.add(query)
		departements = list(departements)

		context['adherents'] = Adherent.objects.filter(actuel=True, federation__in=departements)
		context['departements'] = departements
		context['page_title'] = 'Fichier des adhérents'
		return context



@method_decorator(login_required, name='dispatch')
class AdherentDetail(DetailView):

	model = Adherent
	template_name = 'detail.html'
	pk_url_kwarg = "num_adherent"
	

	def get_context_data(self, **kwargs):
		context = super(AdherentDetail, self).get_context_data(**kwargs)
		print("==============")
		print(kwargs)
		print("==============")
		return context
