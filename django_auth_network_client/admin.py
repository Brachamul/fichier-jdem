from django.contrib import admin

from .models import *

class NetworkUserAdmin(admin.ModelAdmin):
	model = NetworkUser
	list_display = ('user', 'uuid')

admin.site.register(NetworkUser, NetworkUserAdmin)
