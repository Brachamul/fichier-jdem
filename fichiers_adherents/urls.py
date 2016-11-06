from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
	url(r'^televerser/$', views.televersement, name='televersement_du_fichier_adhérent'),
	url(r'^(?P<fichier_id>[0-9]+)/$', views.visualisation_du_fichier_adherent, name='visualisation_du_fichier_adherent'),
	url(r'^actifs/$', views.liste_des_adherents_actifs, name='liste_des_adherents_actifs')
]