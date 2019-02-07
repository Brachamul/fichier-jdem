from django.conf import settings
from django.core.mail import send_mail, send_mass_mail
from django.urls import reverse
import textwrap

from .models import *



def prevenir_du_chargement_dun_nouveau_fichier() :
	
	''' Après chargement d'un nouveau fichier, un email est envoyé aux utilisateurs
	ayant droit de lecture sur le fichier'''

	# TODO : customiser pour dire le nombre de nouveaux adhérents et compagnie

	email_multiple_users(
		users = User.objects.filter(reader=True),
		title = 'Un nouveau fichier adhérent est disponible !',
		text = \
		'''
		Un nouveau fichier est désormais disponible !
		Retrouvez-le dès maintenant : {url}
		'''.format(url=settings.EMAIL_ROOT + reverse('fichier__adherents'))
		)



def email_multiple_users(users, title, text) :

	''' Write an email to a list of users, with the given title and text.
	This can't be an HTML email, and the email's text can't be customized'''

	messages = []

	for user in users :
		message = build_message(user, title, text)
		messages.append(message)

	if settings.DEBUG :
		try :
			send_mass_mail(messages)
		except :
			pass
	else :
		send_mass_mail(messages)



def email_user(user, title, text) :

	message = build_message(user, title, text)

	if settings.DEBUG :
		try :
			send_mail(message)
		except :
			pass
	else :
		send_mail(message)



def build_message(user, title, text):

	''' Builds a message tuple based on the receiving user,
	the email title and the email body text. '''

	subject = '[JDem] ' + title

	text = \
		'''
		Bonjour {},
		{}
		-
		L'équipe du Secrétariat Général des Jeunes Démocrates
		federations@jeunes-democrates.org

		'''.format(user.first_name, text)

	text = textwrap.dedent(text) # removes useless indentations from the email text

	from_email = settings.EMAIL_FROM

	recipient_list = [user.email,]

	message = ( subject, text, from_email, recipient_list )

	return message
