from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView

admin.site.site_header = 'Fichier JDem - Administration'

urlpatterns = [
	url('^', include('django.contrib.auth.urls')),
	url(r'^auth/', include('network_auth_client.urls')),
	url(r'^arriere-boutique/', admin.site.urls, name='admin'),
	url(r'^fichier/', include('fichiers_adherents.urls')),
	url(r'^phoning/', include('phoning.urls')),
	url(r'^$', RedirectView.as_view(url="/phoning", permanent=False)),
]