import random, ast
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from fichiers_adherents.models import Adherent, Note, WrongNumber, adherents_actuels

from .models import *
from .forms import *



def getRandomInstance(QuerySet, filter=False):
	if QuerySet.count() < 1 :
		# RAISE ERROR
		pass
	random_idx = random.randint(0, QuerySet.count() - 1)
	return QuerySet[random_idx]

# Redirects root URL to list of operations
def phoning(request):
	# TODO : maybe redirect back home and say nothing in progress
	return redirect('phoning_operations')



@method_decorator(login_required, name='dispatch')
class OperationsList(ListView):

	model = Operation
	template_name = 'list.html'

	def get_context_data(self, **kwargs):
		context = super(OperationsList, self).get_context_data(**kwargs)
		context['object_list'] = authorized_phoning_operations(self.request.user)
		context['page_title'] = 'Opérations en cours'
		context['url_by_id'] = True
		context['admin_url'] = reverse('admin:phoning_operation_changelist')
		return context

def authorized_phoning_operations(user):
	return Operation.objects.filter(valid_until__gt=datetime.now(), authorized_users=user)

@method_decorator(staff_member_required, name='dispatch')
class OperationTargets(ListView):

	model = Adherent
	template_name = 'list.html'

	def get_context_data(self, **kwargs):
		context = super(OperationTargets, self).get_context_data(**kwargs)
		operation = Operation.objects.get(pk=self.kwargs['operation_id'])
		context['page_title'] = "Membres ciblés par l'opération"
		query = ast.literal_eval(operation.query) # transform string query into dictionary
		context['object_list'] = Adherent.objects.filter(**query)
		context['url_by_id'] = True
		context['url_prefix'] = reverse('admin:fichiers_adherents_adherent_changelist') # changelist because addinng id after
		context['admin_url'] = reverse('admin:phoning_operation_change', args=(operation.id,))
		return context



@login_required
def coordonnees(request, operation_id):
	operation = get_object_or_404(Operation, pk=operation_id)
	if request.user not in operation.authorized_users.all() :
		messages.error(request, "Vous n'êtes pas encore autorisé à participer à cette opération.")
		return redirect('phoning')
	elif operation.valid_until < datetime.now() :
		messages.error(request, "Cette opération de phoning est arrivée à son terme.")
		return redirect('phoning')
	elif not Adherent.objects.count() : 
		messages.error(request, "Il n'y a aucun adhérent dans la base.")
		return redirect('phoning')
	else :
		if request.method == "POST" :
			num_adherent = request.POST.get('num_adherent')
			fichier = FichierAdherents.objects.latest()
			adherent = Adherent.objects.get(num_adherent=num_adherent, fichier=fichier)
			# Check if call was successful or not
			if request.POST.get('call_successful') :
				operation.targets_called_successfully.add(adherent)
			else :
				operation.targets_called_successfully.remove(adherent)
			# Check if number was wront or not
			if request.POST.get('wrong_number') :
				operation.targets_with_wrong_number.add(adherent)
				new_wrong_number = WrongNumber(adherent=adherent, reported_by=request.user)
				new_wrong_number.save()
			else :
				operation.targets_with_wrong_number.remove(adherent)
			if request.POST.get('note') :
				new_note = Note(num_adherent=adherent.num_adherent, author=request.user, text=request.POST.get('note'))
				new_note.save()
		else:
			time_threshold = datetime.now() - timedelta(minutes=20) # 20 minutes ago
			recentRequests = UserRequest.objects.filter(user=request.user).exclude(date__lt=time_threshold)
			if recentRequests.count() > operation.max_requests :
				messages.error(request, "Vous avez réalisé plus de {} requêtes en moins de 20 minutes. Il vous faudra désormais attendre un peu.".format(operation.max_requests))
				return redirect('phoning')
			else :
				query = ast.literal_eval(operation.query) # admin-written query transformed into useable filter
				adherents_called_successfully = operation.targets_called_successfully.all()
				adherents_with_wrong_number = operation.targets_with_wrong_number.all()
				operation_targets = adherents_actuels().filter(**query)\
					.exclude(pk__in=adherents_called_successfully)\
					.exclude(pk__in=adherents_with_wrong_number)
				if operation_targets.count() < 1 : 
					messages.success(request, "Tous les adhérents de cette opération ont déjà été contactés !")
					return redirect('phoning')
				adherent = getRandomInstance(operation_targets)
			newRequest = UserRequest(user=request.user, operation=operation)
			newRequest.save()
	
		return render(request, 'phoning/coordonnees.html', {
			'adherent': adherent,
			'page_title': 'Opération ' + operation.name,
			'wrong_number': operation.targets_with_wrong_number.filter(pk=adherent.pk),
			'call_successful': operation.targets_called_successfully.filter(pk=adherent.pk),
			})
