# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .models import *



@method_decorator(login_required, name='dispatch')
class Profile(DetailView):

	''' Displays a person's profile, based on data from various sources '''

	model = Member
	template_name = 'profiles/profile.html'
	pk_url_kwarg = "num_adherent"

	def dispatch(self, request, *args, **kwargs):
		# TODO : check if belongs to users i am authorized to see
		# TODO : chef if is still in latest fichier
		try : cnil = Cnil.objects.get(user=request.user)
		except ObjectDoesNotExist : return redirect('fichier__declaration_cnil')
		else: return super(Profile, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(Profile, self).get_context_data(**kwargs)
		adherent = self.get_object().derniere_occurence_fichier()
		context['page_title'] = adherent.nom_courant()
		context['adherent'] = adherent
		return context


@login_required
def add_note(request, num_adherent):
	''' Save note '''
	member = get_object_or_404(Member, pk=num_adherent)
	if request.method == "POST" :
		note_text = request.POST.get('note')
		if note_text:
			# user has written a note, so we add it to the member's profile
			new_note = Note(member=member, author=request.user, text=note_text)
			new_note.save()
	return redirect(reverse('profil', kwargs={'num_adherent': num_adherent}))