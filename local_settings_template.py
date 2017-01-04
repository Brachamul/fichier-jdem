# AUTH NETWORK SETTINGS
AUTH_NETWORK_URL = 'http://localhost:8007/'
AUTH_NETWORK_KEY = '686183c4-370f-44dd-85ce-b42ab2fe3c76'
AUTH_NETWORK_SECRET = '7b1f56d6-ed7e-4338-bcf6-f3bcdf2238cb'

# STANDARD SETTINGS
SITE_URL = 'localhost' # use http:// in production
ALLOWED_HOSTS = [SITE_URL, ]
SECRET_KEY = 'many_potatoes'
DEBUG = True
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