from django.contrib import admin

from .models import *

class NetworkUserAdmin(admin.ModelAdmin):
	model = NetworkUser

admin.site.register(NetworkUser, NetworkUserAdmin)
