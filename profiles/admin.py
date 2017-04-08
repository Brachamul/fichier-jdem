from django.contrib import admin

from .models import *



class NoteAdmin(admin.ModelAdmin):
	model = Note
	list_per_page = 250
	list_display = ("member", "logged_by", "text", "date")

admin.site.register(Note, NoteAdmin)

class WrongNumberAdmin(admin.ModelAdmin):
	model = WrongNumber
	list_per_page = 250
	list_display = ("member", "logged_by", "date")

admin.site.register(WrongNumber, WrongNumberAdmin)

class SuccessfulCallAdmin(admin.ModelAdmin):
	model = SuccessfulCall
	list_per_page = 250
	list_display = ("member", "logged_by", "date")

admin.site.register(SuccessfulCall, SuccessfulCallAdmin)

class LeftMessageAdmin(admin.ModelAdmin):
	model = LeftMessage
	list_per_page = 250
	list_display = ("member", "logged_by", "date")

admin.site.register(LeftMessage, LeftMessageAdmin)



class NotesInline(admin.TabularInline):
	model = Note
	extra = 1

class MemberAdmin(admin.ModelAdmin):
	model = Member
	readonly_fields = ("id",)
	list_display = ("id", "__str__")
	inlines = [NotesInline, ]

admin.site.register(Member, MemberAdmin)