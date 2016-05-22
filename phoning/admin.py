from django.contrib import admin

from .models import *



class OperationAdmin(admin.ModelAdmin):
	model = Operation
	list_per_page = 25
	list_display = ("name", "query", "valid_until",)
	readonly_fields = ("slug", "created_by", "created",)

admin.site.register(Operation, OperationAdmin)



class UserRequestAdmin(admin.ModelAdmin):
	model = UserRequest
	list_per_page = 2000
	list_display = ("user", "date")

admin.site.register(UserRequest, UserRequestAdmin)