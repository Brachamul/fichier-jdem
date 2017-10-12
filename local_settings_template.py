# STANDARD SETTINGS
SITE_URL = 'localhost' # use http:// in production
ALLOWED_HOSTS = [SITE_URL, ]
SECRET_KEY = 'many_potatoes'
DEBUG = True

# EMAIL SETTINGS
EMAIL_SUBJECT_PREFIX = "[Fichier JDem] "
EMAIL_USE_TLS = False
EMAIL_HOST = 'smtp.jdem.fr'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'fichier@jdem.fr'
EMAIL_HOST_PASSWORD = 'XXX'
EMAIL_ROOT = 'http://localhost:8008'
EMAIL_FROM = 'Fichier JDem <fichier@jdem.fr>'



# DJANGO AUTH NETWORK CONFIG

import textwrap
def subject_generator(username):
	# convert to kwargs maybe
	subject = '[Fiji] ' + '{} a créé un compte !'.format(username)

def text_generator(username):
	# convert to kwargs maybe
	text = \
		'''

		{} vient de créer un compte sur http://fichier.jdem.fr.
		Si nécessaire, vous pouvez désormais lui accorder des droits sur une partie du fichier.
		
		-
		Message automatique envoyé par Fiji
		
		'''.format(username)
	text = textwrap.dedent(text) # removes useless indentations from the email text
	return text

DJANGO_AUTH_NETWORK_CONFIG = {
	'URL': '', # e.g. : 'http://localhost:8007/'
	'KEY': '', # UUID
	'SECRET' : '', # UUID
	'WARN_WHEN_NEW_ACCOUNT': {
		'SUBJECT_GENERATOR': subject_generator,
		'TEXT_GENERATOR': text_generator,
		'FROM_EMAIL': EMAIL_FROM,
		'RECIPIENT_LIST': ['',],
	}
}


# LOGGING SETTINGS
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'timestamped': {
			'format': '%(levelname)s %(asctime)s %(message)s'
		}
	},
	'handlers': {
		'file': {
			'level': 'DEBUG',
			'class': 'logging.FileHandler',
			'filename': 'debug.log',
			'formatter': 'timestamped',
		},
	},
	'loggers': {
		'django': {
			'handlers': ['file'],
			'level': 'DEBUG',
			'propagate': True,
		},
	},
}

#	CSRF_COOKIE_SECURE = False
#	SESSION_COOKIE_SECURE = False
#	CSRF_COOKIE_HTTPONLY = False