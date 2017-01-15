# AUTH NETWORK SETTINGS
AUTH_NETWORK_URL = 'http://localhost:8007/'
AUTH_NETWORK_KEY = '6868e1d3-a21b-47fb-a83d-2e4f1baedb14'
AUTH_NETWORK_SECRET = '9174e12e-15b0-487e-859c-d271053df9de'

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