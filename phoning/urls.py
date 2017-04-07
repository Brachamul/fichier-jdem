from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
	url(r'^$', views.phoning, name='phoning'),
	url(r'^operations/$', views.OperationsList.as_view(), name='phoning_operations'),
	url(r'^operations/(?P<operation_id>[0-9]+)/$', views.coordonnees, name='coordonnees'),
	url(r'^operations/(?P<operation_id>[0-9]+)/liste/$', views.OperationTargets.as_view(), name='operation_targets'),
	url(r'^operations/test/$', views.test, name='phoning__test'),
]