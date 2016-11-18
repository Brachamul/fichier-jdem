from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
	url(r'^televerser/$', views.televersement, name='televersement_du_fichier_adhérent'),
	url(r'^(?P<fichier_id>[0-9]+)/$', views.visualisation_du_fichier_adherent, name='visualisation_du_fichier_adherent'),
	url(r'^query-checker/$', views.query_checker, name='fichier__query_checker'),
	url(r'^adherents/$', views.ListeDesAdherents.as_view(), name='fichier__adherents'),
	url(r'^adherents/(?P<num_adherent>[0-9]+)/$', views.VueAdherent, name='adherent'),
	url(r'^adherents/actualiser/$', views.actualiser_les_adherents, name='fichier__actualiser'),
	url(r'^$', RedirectView.as_view(permanent=False, url='adherents/'), name='fichier'),
]