=====
Django Auth Network Client
=====

Django Auth Network (DAN) is a set of two packages that create Google and Facebook-style authentication, but using your own provider instead of Google or Facebook.

The DAN Provider package allows you to run the authentication network, and the DAN Client package enables creating accounts and logging in through DANP.

First, add 'django-auth-network-client' to your installed apps :

	# settings.py
	INSTALLED_APPS += ['django-auth-network-client',]

Second, set the following required values :

	# local_settings.py
	AUTH_NETWORK_URL	= 'PLEASE SET AUTH_NETWORK_URL' # e.g. : 'http://localhost:8007/'
	AUTH_NETWORK_KEY	= 'PLEASE SET AUTH_NETWORK_KEY' # UUID
	AUTH_NETWORK_SECRET	= 'PLEASE SET AUTH_NETWORK_SECRET' # UUID

The URL must point to your DAN provider. You need to add your app on the DAN provider in order to generate a Key and Secret for your app.

WARNING : these values should be secret, so don't upload them to github. If your code is open-source, make sure you set the `AUTH_NETWORK_SECRET` value in your local settings. See [this stackoverflow answer]('http://stackoverflow.com/a/4909964/3083792').

Finally, you'll need to set up your DAN urls as well as `LOGIN_URL` in your settings file.

	# urls.py
	urlpatterns = [
		...
		url(r'^auth/', include('django-auth-network-client.urls')),
		...
	]

	# settings.py
	LOGIN_URL = '/auth/'

There, that should be all. Now, go to yourapp.com/auth/ or to a page that requires login to see DAN in action.