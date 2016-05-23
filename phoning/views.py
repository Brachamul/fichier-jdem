import random, ast
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from fichiers_adherents.models import Adherent, Note

from .models import *
from .forms import *



time_threshold = datetime.now() - timedelta(minutes=20)

def getRandomInstance(Model, filter=False):
	if Model.objects.count() < 1 :
		# RAISE ERROR
		pass
	random_idx = random.randint(0, Model.objects.count() - 1)
	return Model.objects.all()[random_idx]

# Redirects root URL to list of operations
def phoning(requests):
	return redirect('phoning_operations')



@method_decorator(login_required, name='dispatch')
class OperationsList(ListView):

	model = Operation
	template_name = 'list.html'

	def get_context_data(self, **kwargs):
		context = super(OperationsList, self).get_context_data(**kwargs)
		context['page_title'] = 'Opérations en cours'
		context['url_by_id'] = True
		context['admin_url'] = urlresolvers.reverse('admin:phoning_operation_changelist')
		return context



@method_decorator(staff_member_required, name='dispatch')
class OperationTargets(ListView):

	model = Adherent
	template_name = 'list.html'

	def get_context_data(self, **kwargs):
		context = super(OperationTargets, self).get_context_data(**kwargs)
		operation = Operation.objects.get(pk=self.kwargs['operation_id'])
		context['page_title'] = "Membres ciblés par l'opération"
		query = ast.literal_eval(operation.query) # transform string query into dictionary
		context['object_list'] = Adherent.objects.filter(**query) # **{operation.query}
		context['url_by_id'] = True
		context['url_prefix'] = urlresolvers.reverse('admin:fichiers_adherents_adherent_changelist') # changelist because addinng id after
		context['admin_url'] = urlresolvers.reverse('admin:phoning_operation_change', args=(operation.id,))
		return context



@login_required
def coordonnees(request, operation_id):
	operation = get_object_or_404(Operation, pk=operation_id)
	if not Adherent.objects.count() : 
		messages.error(request, "Il n'y a aucun adhérent dans la base.")
		return redirect('phoning')
	else :
		if request.method == "POST":
			num_adherent = request.POST.get('num_adherent')
			adherent = Adherent.objects.get(num_adherent=num_adherent)
			if request.POST.get('note') :
				new_note = Note(target=adherent, author=request.user, text=request.POST.get('note'))
				new_note.save()
		else:
			recentRequests = UserRequest.objects.filter(user=request.user).exclude(date__lt=time_threshold).count()
			if recentRequests > 10 :
				adherent = False
				messages.error(request, "Vous avez réalisé plus de 10 requêtes en moins de 20 minutes. Il vous faudra désormais attendre un peu.")
			else :
				adherent = getRandomInstance(Adherent)
			newRequest = UserRequest(user=request.user, operation=operation)
			newRequest.save()
	
		return render(request, 'phoning/coordonnees.html', {
			'adherent': adherent,
			'admin_url': 'admin:fichiers_adherents_adherent_change',
			'page_title': 'Opération ' + operation.name
			})
