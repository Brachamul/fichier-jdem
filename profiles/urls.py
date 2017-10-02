from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
	url(r'^(?P<num_adherent>[0-9]+)/add-note/$', views.add_note, name='add_note'),
	url(r'^(?P<num_adherent>[0-9]+)/$', views.Profile.as_view(), name='profil'),
	url(r'^$', RedirectView.as_view(permanent=False, url='/'), name='crm'),
]