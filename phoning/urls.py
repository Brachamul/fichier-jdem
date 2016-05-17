from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
	url(r'^$', views.phoning, name='phoning'),
	url(r'^operations/$', views.phoning_operations, name='phoning_operations'),
#	url(r'^$', views.coordonees, name='coordonees'),
]