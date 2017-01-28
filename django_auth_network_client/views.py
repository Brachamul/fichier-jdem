import logging, json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView, ListView, FormView, CreateView

from .models import *



class WrongSecret(Exception): pass

def Warn(request):
	''' Tell the user they will get redirected '''
	return render(request, 'django_auth_network_client/warn.html')

def Identify(request):
	''' Let's go to the provider and log into it to ask for authorization '''
	return redirect(settings.AUTH_NETWORK_URL + 'identify/' + settings.AUTH_NETWORK_KEY)

@csrf_exempt # TODO : make sure this isn't stupid
def SetToken(request, user_uuid):
	
	secret = request.POST.get('secret')
	new_token = request.POST.get('new_token')
	user_details_json = request.POST.get('user_details')
	user_details = json.loads(user_details_json)

	# secretly sets a new authentication token as the user's password
	if secret != settings.AUTH_NETWORK_SECRET : raise WrongSecret
	network_user, created = NetworkUser.objects.get_or_create(uuid=uuid.UUID(user_uuid))
	try:
		network_user.update_user_details(user_details)
	except UserCreationError:
		# user creation failed, deleting network_user
		network_user.delete()
		return HttpResponse(status=409)
	network_user.user.set_password(new_token)
	network_user.user.save()
	return HttpResponse('Token succesfully set to ' + str(new_token))

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
	return render(request, 'test.html', { 'items': [
		{'username': network_user.user.username,},
		{'token': token,},
		]})