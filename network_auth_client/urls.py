from django.conf.urls import url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
	url(r'^$', views.Identify, name='network_auth'),
	url(r'^set-token/(?P<user_uuid>[\x00-\x7F]+)/(?P<token>[\x00-\x7F]+)/(?P<app_secret>[\x00-\x7F]+)/$', views.SetToken, name='network_auth_set_token'),
	url(r'^callback/(?P<user_uuid>[\x00-\x7F]+)/(?P<token>[\x00-\x7F]+)/$', views.CallBack, name='network_auth_callback'),
]