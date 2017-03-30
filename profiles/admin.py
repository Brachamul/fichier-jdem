from django.contrib import admin

from .models import *



class MemberAdmin(admin.ModelAdmin):
	model = Member
	readonly_fields = ("id",)

admin.site.register(Member, MemberAdmin)