from django.contrib import admin

from .models import *

class UserRequestAdmin(admin.ModelAdmin):
	model = UserRequest
	list_per_page = 2000
	list_display = ("user", "date")

admin.site.register(UserRequest, UserRequestAdmin)