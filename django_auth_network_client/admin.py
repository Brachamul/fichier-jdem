from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *



class NetworkUserAdmin(admin.ModelAdmin):
	model = NetworkUser
	list_display = ('user', 'uuid')

admin.site.register(NetworkUser, NetworkUserAdmin)


class CustomUserAdmin(UserAdmin):

	''' Some user fields are automatically set by the DAN provider.
	This replacement of the normal user admin disables the ability
	to change username, first name, last name and email data manually '''

	def __init__(self, *args, **kwargs):
		super(UserAdmin,self).__init__(*args, **kwargs)

	readonly_fields = ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined', )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)