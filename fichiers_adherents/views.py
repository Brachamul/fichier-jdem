# -*- coding: utf-8 -*-
import csv
import logging
import sys

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max, F
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext

#	from datascope.models import mettre_a_jour_les_federations

from .models import *
from .forms import *

@login_required
def dashboard(request):
	if request.user.has_perm('fichiers_adherents.peut_televerser'):
	

@login_required
def televersement(request):
	if request.user.has_perm('fichiers_adherents.peut_televerser'):
		if request.method == "POST":
			upload_form = TéléversementDuFichierAdherentForm(request.POST, request.FILES)
			if upload_form.is_valid():
				logging.info("A new adherent file was uploaded by {user}.".format(user=request.user).encode('utf8'))
				fichier = request.FILES['fichier_csv']
				importateur = request.user
				slug = request.POST.get('slug')
				date = request.POST.get('date')
				fichier.name = ('fichiers_adherents/' + slug + '.csv') # renomme le fichier grâce au slug
				nouveau_fichier = FichierAdherents(importateur=importateur, fichier_csv=fichier, date=date, slug=slug) # rattache le fichier à la base des fichiers importés
				nouveau_fichier.save()
				importation(nouveau_fichier) # Importe les données du fichier dans la base "Adherent"
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
def liste_des_adherents_actifs(request) :
	print(adherents_actifs())
	adherents = []
	for adherent in adherents_actifs():
		print(adherent.prenom)

	return HttpResponse(adherents)



@login_required
def query_checker(request, query):
	if request.user.has_perm('fichiers_adherents.lecture_fichier_national'):
		query = ast.literal_eval(operation.query) # transform string query into dictionary
		object_list = Adherent.objects.filter(**query)
		admin_url = reverse('admin:fichiers_adherents_adherent_changelist')
		return render(request, 'list.html', {
			'page_title': "Query Checker",
			'object_list': object_list,
			'admin_url': admin_url,
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
			nouvel_adherent = Adherent(fichier=fichier)
			nouvel_adherent.federation = row['Fédération']
			nouvel_adherent.date_premiere_adhesion = process_csv_date(row['Date première adhésion'])
			nouvel_adherent.date_derniere_cotisation = process_csv_date(row['Date dernière cotisation'])
			nouvel_adherent.num_adherent = row['Num adhérent']
			nouvel_adherent.genre = row['Genre']
			nouvel_adherent.nom = row['Nom']
			nouvel_adherent.prenom = row['Prénom']
			nouvel_adherent.adresse1 = row['Adresse 1']
			nouvel_adherent.adresse2 = row['Adresse 2']
			nouvel_adherent.adresse3 = row['Adresse 3']
			nouvel_adherent.adresse4 = row['Adresse 4']
			nouvel_adherent.code_postal = row['Code postal']
			nouvel_adherent.ville = row['Ville']
			nouvel_adherent.pays = row['Pays']
			nouvel_adherent.npai = row['NPAI']
			nouvel_adherent.date_de_naissance = process_csv_date(row['Date de naissance'])
			nouvel_adherent.profession = row['Profession']
			nouvel_adherent.tel_portable = row['Tel portable']
			nouvel_adherent.tel_bureau = row['Tel bureau']
			nouvel_adherent.tel_domicile = row['Tel domicile']
			nouvel_adherent.email = row['Email'].lower()
			nouvel_adherent.mandats = row['Mandats'].replace("\n", ", ")
			nouvel_adherent.commune = row['Commune']
			nouvel_adherent.commune = row['Canton']
#			ancien_adherent = Adherent.objects.filter(
#				num_adherent=nouvel_adherent.num_adherent,
#				date_derniere_cotisation=nouvel_adherent.date_derniere_cotisation
#				).latest()
			if nouvel_adherent != ancien_adherent :
				nouvel_adherent.save()

def process_csv_date(csv_date):
	if csv_date : return datetime.strptime(csv_date, '%d/%m/%Y').date()
	else : return None


def adherents_actifs() :
	''' liste le nombre d'adhérents qui seraient introduits par ce fichier '''
	return Adherent.objects.annotate(max_date=Max('date_derniere_cotisation')).filter(date_derniere_cotisation=F('max_date'))
	# can't use Adherent.objects.all().order_by('date_derniere_cotisation').distinct('num_adherent') on sqlite, so using .values_list('num_adherent', flat=True).distinct() instead

