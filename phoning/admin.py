from django.contrib import admin

from .models import *



class OperationAdmin(admin.ModelAdmin):
	model = Operation
	list_per_page = 25
	list_display = ("name", "query", "valid_until",)
	readonly_fields = ("created_by", "created",)

	def save_model(self, request, obj, form, change):
		# When creating a new object, set the creator field.
	    if not change:
	        obj.created_by = request.user
	    obj.save()

admin.site.register(Operation, OperationAdmin)



class UserRequestAdmin(admin.ModelAdmin):
	model = UserRequest
	list_per_page = 2000
	list_display = ("user", "date")

admin.site.register(UserRequest, UserRequestAdmin)