import random
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext
from fichiers_adherents.models import Adherent, Note

from .models import *
from .forms import *

time_threshold = timezone.now() - timedelta(minutes=20)

def getRandomInstance(Model, filter=False):
	random_idx = random.randint(0, Model.objects.count() - 1)
	return Model.objects.all()[random_idx]

@login_required
def coordonees(request):
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
		newRequest = UserRequest(user=request.user)
		newRequest.save()

	return render(request, 'phoning/coordonees.html', {'adherent': adherent})
