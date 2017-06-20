'''
Django settings, generated using Django 1.9.4.
'''

import os

# Build paths inside the project like this: os.path.join(PROJECT_ROOT, ...)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wb8ua=u$k3cpv*b&#63-@9d!0h)mgozggi8-(%xvxg4i1a-5&x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
APPEND_SLASH = True

# Application definition

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'bootstrap3', # django-bootstrap3
	'fichiers_adherents',
	'profiles',
	'phoning',
]

# Make AutoSlugs use unicode characters
from slugify import slugify
AUTOSLUG_SLUGIFY_FUNCTION = slugify

MIDDLEWARE_CLASSES = [
	'django.middleware.gzip.GZipMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
#	'_project.middleware.LoginRequiredMiddleware', # TODO : reactivate
]


ROOT_URLCONF = '_project.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [ os.path.join(PROJECT_ROOT, 'static/templates/'), ],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = '_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(PROJECT_ROOT, 'db.sqlite3'),
	}
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join((PROJECT_ROOT), "_static_root")
MEDIA_ROOT = os.path.join((PROJECT_ROOT), "_media_root")
STATICFILES_DIRS = (
	os.path.join((PROJECT_ROOT), "static", "static"),
)

LOGIN_URL = '/auth/'
LOGIN_REDIRECT_URL = '/'

from django.contrib import messages
MESSAGE_TAGS = { messages.ERROR: 'danger' }



# CENTRIFUGE NETWORK AUTH

INSTALLED_APPS += ['django_auth_network_client',]
''' The following values must be set in local settings '''
NETWORK_AUTH_URL	= 'PLEASE SET NETWORK_AUTH_URL' # e.g. : 'http://localhost:8007/'
NETWORK_AUTH_KEY	= 'PLEASE SET NETWORK_AUTH_KEY' # UUID
NETWORK_AUTH_SECRET	= 'PLEASE SET NETWORK_AUTH_SECRET' # UUID


# WAGTAIL CMS

INSTALLED_APPS += [
	'wagtail.wagtailforms',
	'wagtail.wagtailredirects',
	'wagtail.wagtailembeds',
	'wagtail.wagtailsites',
	'wagtail.wagtailusers',
	'wagtail.wagtailsnippets',
	'wagtail.wagtaildocs',
	'wagtail.wagtailimages',
	'wagtail.wagtailsearch',
	'wagtail.wagtailadmin',
	'wagtail.wagtailcore',
	'modelcluster',
	'taggit',
	'guide', # our local wagtail app
	]

MIDDLEWARE_CLASSES += [
	'wagtail.wagtailcore.middleware.SiteMiddleware',
	'wagtail.wagtailredirects.middleware.RedirectMiddleware',
	]

WAGTAIL_SITE_NAME = "du guide des responsables de fédérations"

WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_URL # use custom auth, even for CMS access


# EMAILING

INSTALLED_APPS += ['anymail',]

DEFAULT_FROM_EMAIL = "Fiji - le fichier JDem <fichier@jdem.fr>"
EMAIL_SHOULD_FAIL_SILENTLY = True 

EMAIL_BACKEND = "anymail.backends.mailgun.MailgunBackend"  # or sendgrid.SendGridBackend, or...

# Note that the "ANYMAIL" variable including API key and sender domain must be set in local settings


##########################
#  Settings localisables :
##########################

# import local_settings if exist
try: from local_settings import *
except ImportError: pass