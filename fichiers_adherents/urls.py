from django.conf.urls import patterns, url

from . import views

urlpatterns = [
	url(r'^televerser/$', views.televersement, name='televersement_du_fichier_adhérent'),
	url(r'^(?P<fichier_id>[0-9]+)/$', views.visualisation_du_fichier_adherent, name='visualisation_du_fichier_adherent'),
	url(r'^(?P<fichier_id>[0-9]+)/charger$', views.activer_le_fichier_adherent, name='activer_le_fichier_adherent'),
]