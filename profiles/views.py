# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView

from .models import *



@method_decorator(login_required, name='dispatch')
class Profile(DetailView):

	model = Member
	template_name = 'profiles/profile.html'

	def dispatch(self, request, *args, **kwargs):
		# TODO : check if belongs to users i am authorized to see
		# TTODO : chef if is still in latest fichier
		try : cnil = Cnil.objects.get(user=request.user)
		except ObjectDoesNotExist : return redirect('fichier__declaration_cnil')
		else: return super(ListeDesAdherents, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(Profile, self).get_context_data(**kwargs)
		adherent = self.derniere_occurence_fichier()
		context['page_title'] = adherent.nom_courant()
		context['adherent'] = adherent
		return context