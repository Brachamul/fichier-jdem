from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
	url(r'^(?P<pk>[0-9]+)/$', views.Profile.as_view(), name='profil'),
	url(r'^$', RedirectView.as_view(permanent=False, url='/'), name='crm'),
]