from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
	url(r'^$', views.Warn, name='auth_network'),
	url(r'^identify/$', views.Identify, name='auth_network_identify'),
	url(r'^set-token/(?P<user_uuid>[\x00-\x7F]+)/$', views.SetToken, name='auth_network_set_token'),
	url(r'^callback/(?P<user_uuid>[\x00-\x7F]+)/(?P<token>[\x00-\x7F]+)/$', views.CallBack, name='auth_network_callback'),
]