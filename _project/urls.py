from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView

admin.site.site_header = 'Fichier JDem - Administration'

urlpatterns = [
	url('^', include('django.contrib.auth.urls')),
	url(r'^auth/', include('django_auth_network_client.urls')),
	url(r'^arriere-boutique/', admin.site.urls, name='admin'),
	url(r'^fichier/', include('fichiers_adherents.urls')),
	url(r'^phoning/', include('phoning.urls')),
	url(r'^profils/', include('profiles.urls')),
#	url(r'^$', RedirectView.as_view(url="/phoning", permanent=False)),
]


# Pages de guide des responsables de fédérations avec Wagtail

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls

urlpatterns += [
	url(r'^cms/login/', RedirectView.as_view(url="/auth/", permanent=False)),
	url(r'^cms/', include(wagtailadmin_urls)),
	url(r'^documents/', include(wagtaildocs_urls)),
	url(r'^', include(wagtail_urls)),
]