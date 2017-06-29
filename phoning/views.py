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

from fichiers_adherents.models import Adherent, adherents_actuels
from profiles.models import Note, WrongNumber, Member

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
		context['page_title'] = 'Phonings en cours'
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

	''' This view pulls an individual from the call list and 
	displays their data so we can interact with them '''

	operation = get_object_or_404(Operation, pk=operation_id)

	if not operation_requirements_are_met(request, operation) :
		# there are several requirements that need to be met before we can show this view
		return redirect('phoning')

	else :
		if request.method == "POST" :
			# the user has triggered an action for this adherent
			num_adherent = request.POST.get('num_adherent')
			try : 
				member = Member.objects.get(id=num_adherent)
			except Member.DoesNotExist:
				messages.error(request, "Cet adhérent n'a pas été retrouvé.")
				return redirect('coordonnees', kwargs={'operation_id': operation_id})
			else :
				process_phoning_action(
					editor = request.user,
					member = member,
					call_successful = request.POST.get('call_successful'),
					wrong_number = request.POST.get('wrong_number'),
					note = request.POST.get('note'),
					)

		else:
			time_threshold = datetime.now() - timedelta(minutes=20) # 20 minutes ago
			recentRequests = UserRequest.objects.filter(user=request.user).exclude(date__lt=time_threshold)
			if recentRequests.count() > operation.max_requests :
				messages.error(request, "Vous avez réalisé plus de {} requêtes en moins de 20 minutes. Il vous faudra désormais attendre un peu.".format(operation.max_requests))
				return redirect('phoning')
			else :
				query = ast.literal_eval(operation.query) # admin-written query transformed into useable filter
				members_called_successfully = operation.targets_called_successfully.all()
				members_with_wrong_number = operation.targets_with_wrong_number.all()
				members_with_no_phone_number = Member.objects.filter(phoneless=True)
				operation_targets = adherents_actuels().filter(**query)\
					.exclude(num_adherent__in=members_called_successfully)\
					.exclude(num_adherent__in=members_with_wrong_number)\
					.exclude(num_adherent__in=members_with_no_phone_number)
				if operation_targets.count() < 1 : 
					messages.success(request, "Tous les adhérents de cette opération ont déjà été contactés !")
					return redirect('phoning')
				operation_targets = Member.objects.filter(pk__in=operation_targets.values('num_adherent'))
				member = getRandomInstance(operation_targets)
			newRequest = UserRequest(user=request.user, operation=operation)
			newRequest.save()
	
		return render(request, 'phoning/coordonnees.html', {
			'member': member,
			'adherent': member.derniere_occurence_fichier(),
			'page_title': operation.name,
			'wrong_number': operation.targets_with_wrong_number.filter(pk=member.pk),
			'call_successful': operation.targets_called_successfully.filter(pk=member.pk),
			})


def operation_requirements_are_met(request, operation):

	requirements_are_met = True

	if not request.user in operation.authorized_users.all() :
		messages.error(request, "Vous n'êtes pas encore autorisé à participer à cette opération.")
		requirements_are_met = False
		
	if operation.valid_until < datetime.now() :
		messages.error(request, "Cette opération de phoning est arrivée à son terme.")
		requirements_are_met = False

	if not Adherent.objects.count() : 
		messages.error(request, "Il n'y a aucun adhérent dans la base.")
		requirements_are_met = False

	return requirements_are_met


def process_phoning_action(editor, member, call_successful, wrong_number, note):

	if call_successful :
		# call was succesful, remove this person from list of people to call on this operation
		operation.targets_called_successfully.add(member)
	else :
		# user has corrected his request to mark the call successful,
		# so adherent will be added back to the list
		operation.targets_called_successfully.remove(member)

	if wrong_number :
		# user says that this adherent's number is wrong
		# we won't do anything about it, but at least keep it in memory
		# so that we can automate something with this one day
		# TODO : make this actually useful
		operation.targets_with_wrong_number.add(member)
		new_wrong_number = WrongNumber(member=member, reported_by=editor)
		new_wrong_number.save()
	else :
		operation.targets_with_wrong_number.remove(member)

	if note:
		# user has written a note, so we add it to the user's profile
		new_note = Note(member=member, author=editor, text=request.POST.get('note'))
		new_note.save()



@staff_member_required
def test(request):
	member = getRandomInstance(Member.objects.all())
	return render(request, 'phoning/coordonnees.html', {
		'member': member,
		'adherent': member.derniere_occurence_fichier(),
		'page_title': 'Opération Test',
		'wrong_number': False,
		'call_successful': False,
		})

