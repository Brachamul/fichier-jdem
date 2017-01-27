# AUTH NETWORK SETTINGS
AUTH_NETWORK_URL = 'http://localhost:8007/'
AUTH_NETWORK_KEY = 'PLEASE_SET_NETWORK_AUTH_KEY'
AUTH_NETWORK_SECRET = 'PLEASE_SET_NETWORK_AUTH_SECRET'

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
EMAIL_HOST_PASSWORD = '-'
EMAIL_ROOT = 'http://localhost:8008'

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