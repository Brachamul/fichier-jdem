import logging, requests, json
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
		# Check if this already registered on this site
		network_user = NetworkUser.objects.get(uuid=uuid.UUID(user_uuid))
	except NetworkUser.DoesNotExist: 
		# Otherwise, create it
		user_details_request = requests.get(settings.NETWORK_AUTH_URL + 'o/get-details/' + settings.NETWORK_AUTH_KEY + '/' + settings.NETWORK_AUTH_SECRET + '/' + user_uuid)
		user_details = json.loads(user_details_request.text) # The user_details_request returns a Response object. Its '.text' is JSON.
		user = User.objects.create_user(**user_details)
		network_user = NetworkUser(user=user, uuid=uuid.UUID(user_uuid))
		network_user.save()
	else :
		# Network user already exists
		user = network_user.user
	user.set_password(token)
	user.save()
	return HttpResponse('Token succesfully set')



def CallBack(request, user_uuid, token):
	# token is checked against new password to see if it matches
	network_user = get_object_or_404(NetworkUser, uuid=user_uuid)
	user = authenticate(username=network_user.user.username, password=token)
	url_to_redirect = request.POST.get('next')
	if not url_to_redirect : url_to_redirect = '/'
	if user is not None:
		if user.is_active:
			login(request, user)
			user.set_unusable_password()
			return redirect(url_to_redirect)
		else :
			messages.error(request, 'account disabled')
	else :
		messages.error(request, 'invalid login')
	return render(request, 'network_auth_client/test.html', { 'username': network_user.user.username, 'token': token, } )