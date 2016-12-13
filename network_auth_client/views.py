import logging, requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, Http404, QueryDict
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView, ListView, FormView, CreateView

from .models import *

class WrongSecret(Exception): pass

def Identify(request):
	''' Let's go to the provider and log into it to ask for authorization '''
	return redirect(settings.NETWORK_AUTH_URL + 'o/identify/' + settings.NETWORK_AUTH_KEY)

@csrf_exempt # TODO : make sure this isn't stupid
def SetToken(request, user_uuid, token, app_secret):
	# secretly sets a new authentication token as the user's password
	if app_secret != settings.NETWORK_AUTH_SECRET : raise WrongSecret
	try :
		network_user = NetworkUser.objects.get(uuid=uuid.UUID(user_uuid))
	except NetworkUser.DoesNotExist: 
		user_details = requests.get(settings.NETWORK_AUTH_URL + 'o/get-details/' + settings.NETWORK_AUTH_KEY + '/' + settings.NETWORK_AUTH_SECRET + '/' + user_uuid)
		user = User.objects.create_user(user_details)
		network_user = NetworkUser(user=user, uuid=uuid.UUID(user_uuid))
		network_user.save()
	else :
		user = network_user.user
	if created : pass # a new user was created !

	User.set_password(token)
	return HttpResponse('Token succesfully set')



def CallBack(request, user_uuid, token):
	# token is checked against new password to see if it matches
	network_user = get_object_or_404(NetworkUser, uuid=user_uuid)
	user = authenticate(username=network_user.user.username, password=token)
	redirect_to = request.POST.get('next')
	if user is not None:
		if user.is_active:
			login(request, user)
			user.set_unusable_password()
			return redirect(next)
		else: messages.error(request, 'account disabled')
	else: messages.error(request, 'invalid login')
	return redirect('/') # TODO : this should go to some sort of error page